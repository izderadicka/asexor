import asyncio
from asexor.raw_socket import PrefixProtocol
from asexor.message import DelegatedCallMessage, CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from asexor.utils import asure_coro_fn
from asexor.config import Config, ConfigError
from asexor.tqueue import TaskSchedulerMixin
from asexor.api import AbstractTaskContext, AbstractBackend
import logging
import traceback
from urllib.parse import urlparse

logger = logging.getLogger('raw_backend')

HS_CODE_OK = b'\x00' 
HS_CODE_AUTH_ERROR = b'\x01' 
HS_CODE_OTHER_ERROR = b'\x02'    

class NoUpdateCallContext(AbstractTaskContext):
    def send(self, task_id, **kwargs):
        pass

class CallContext(AbstractTaskContext):  
    def __init__(self, call_id, session):
        self.call_id = call_id
        self._session = session
        
    def send(self, task_id, **kwargs):
        if not self._session:
            return
        kwargs['task_id']=task_id
        try:
            self._session.send(UpdateMessage(self.call_id, kwargs).as_binary())
        except Exception:
            logger.exception('WS send failed')

class AsexorBackendSession(PrefixProtocol, TaskSchedulerMixin):
    
    def __init__(self, tasks_queue, delegated=False, no_update=False, loop=None):
        PrefixProtocol.__init__(self, loop=loop)
        self._handshake = self.HS_NONE
        self.tasks = tasks_queue
        self.delegated = delegated
        if no_update:
            self.no_update = NoUpdateCallContext()
        else:
            self.no_update = None
    
    HS_NONE = 0
    HS_IN_PROGRESS = 1
    HS_DONE = 2
    HS_ERROR =3
    def frame_received(self, data):
        if self._handshake == self.HS_DONE:
            try:
                if self.delegated:
                    msg = DelegatedCallMessage.from_binary(data)
                else:
                    msg = CallMessage.from_binary(data)
            except:
                logger.exception('Invalid message: %s', data)
                self.protocol_error('Invalid call message')
                return
            self.loop.create_task(self.process_message(msg))
        elif self._handshake == self.HS_NONE:
            #authenticate -  data are token
            self.loop.create_task(self.authenticate(data))
        else:
            self.protocol_error('No data should come until handshake is complete')
            
    async def authenticate(self, token):
        try:
            authenticator = asure_coro_fn(Config.RAW.AUTHENTICATION_PROCEDURE)
        except ValueError:
            logger.error('Configuration error for RAW.AUTHENTICATION_PROCEDURE - not function or coroutine')
            self.send(HS_CODE_OTHER_ERROR)
            self.transport.close()
        user = None
        try:
            user, role = await authenticator(token)
        except:
            logger.exception('Authenticator error')
            
        if not user:
            logger.error('Authentication failure, token: %s', token)
            self.send(HS_CODE_AUTH_ERROR)
            self.transport.close()
            
        else:
            logger.debug('Authentication success, user is %s, role is %s', user, role)
            self.user = user
            self.role = role
            self.send(HS_CODE_OK)
            self._handshake = self.HS_DONE
            
    async def process_message(self, call): 
        if self.no_update:
            ctx = self.no_update
        else:
            ctx = CallContext(call.call_id, self)
        try:
            if self.delegated:
                user = call.user
                role = call.role
                logger.debug('Task %s is delegated for user %s with role %s', call.task_name, user, role)
            else:
                user = self.user
                role = self.role
            if not user:
                raise Exception('User identification is missing, %s', str(call))    
            task_id = await self.schedule_task(
                ctx, user, role, call.task_name, *call.args, **call.kwargs)
            res = ReplyMessage(call.call_id, task_id)
            logger.debug('Sending respose: %s', res)
            self.send(res.as_binary())
        except Exception as e:
            error = str(e) or repr(e)
            tb = traceback.format_exc() if Config.SEND_REMOTE_ERROR_STACK else None
            logger.exception('Task scheduling error')
            self.send(ErrorMessage(call.call_id, error, error_stack=tb).as_binary())
            

class RawSocketAsexorBackend(AbstractBackend):   
    def __init__(self, loop, url, delegated=False, no_update=False): 
        super(RawSocketAsexorBackend, self).__init__(loop)   
        self.url = url
        self.delegated = delegated
        self.no_update = no_update
        
    async def start(self, tasks_queue):
        parsed_url = urlparse(self.url)
        fact = lambda: AsexorBackendSession(tasks_queue, loop=self.loop, delegated=self.delegated, no_update=self.no_update)
        
        if parsed_url.scheme =='tcp':
            coro=self.loop.create_server(fact,
                                    host=parsed_url.hostname, port=parsed_url.port,
                                    backlog = 128)
        elif parsed_url.scheme =='unix' or parsed_url.scheme == '':
            coro = self.loop.create_unix_server(fact, path= parsed_url.path)
            
        self.server = await coro
        logger.info('Raw backend started on %s', self.url)
        
        
    async def stop(self):
        self.server.close()
        await self.server.wait_closed()