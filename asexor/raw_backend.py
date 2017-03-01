import asyncio
from asexor.raw_socket import PrefixProtocol
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from asexor.utils import asure_coro_fn
from asexor.config import Config, ConfigError
from asexor.tqueue import TaskSchedulerMixin
from asexor.api import AbstractTaskContext
import logging
import traceback

logger = logging.getLogger('raw_backend')

HS_CODE_OK = b'\x00' 
HS_CODE_AUTH_ERROR = b'\x01' 
HS_CODE_OTHER_ERROR = b'\x02'    

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
    
    def __init__(self, tasks_queue, loop=None):
        PrefixProtocol.__init__(self, loop=loop)
        self._handshake = self.HS_NONE
        self.tasks = tasks_queue
    
    HS_NONE = 0
    HS_IN_PROGRESS = 1
    HS_DONE = 2
    HS_ERROR =3
    def frame_received(self, data):
        if self._handshake == self.HS_DONE:
            try:
                msg = CallMessage.from_binary(data)
            except:
                logger.debug('Invalid message: %s', data)
                self.protocol_error('Invalid call message')
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
            self.user = user
            self.role = role
            self._handshake = self.HS_DONE
            
    async def process_message(self, call): 
        ctx = CallContext(call.call_id, self)
        try:
            task_id = self.schedule_task(
                ctx, self.user, self.role, call.task_name, *call.args, **call.kwargs)
            res = ReplyMessage(call.call_id, task_id)
            logger.debug('Sending respose: %s', res)
            self.send(res.as_binary())
        except Exception as e:
            error = str(e) or repr(e)
            tb = traceback.format_exc()
            logger.exception('Task scheduling error')
            self.send(ErrorMessage(call.call_id, error, error_stack=tb).as_binary())
        
        
            