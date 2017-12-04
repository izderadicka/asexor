import aiohttp
from aiohttp import web
import aiohttp_cors
import asyncio
import time
import os
import base64
import logging
import re
import types

from asexor.config import Config, ConfigError

from asexor.tqueue import TaskSchedulerMixin
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from asexor.api import AbstractTaskContext, AbstractHttpBackend
import traceback
logger = logging.getLogger('lp_backend')

class Session:
    __slots__ = ('ts', 'retire_task', 'messages', '_ready', 'user', 'role', 'active')
    def __init__(self, user, role, retire_task, loop=None):
        self.ts = time.time()
        self.messages = []
        self.retire_task = retire_task
        self.role = role
        self.user = user
        self.active = True
        self._ready = asyncio.Event(loop=loop)
    
    def release_wait(self):
        self._ready.set()
        
    def add_message(self, msg):
        if self.active:
            self.messages.append(msg)
            self._ready.set()
        
    async def get_messages(self):
        await self._ready.wait()
        messages = self.messages
        #assert messages
        self.messages = []
        self._ready.clear()
        return messages
        
        
async def authenticate(request):
    token = request.headers.get('Authorization')
    
    if token:
        m = re.match(r'Bearer\s+(.+)', token, re.IGNORECASE)
        if m:
            token = m.group(1)
        else:
            token = None
            
    if not token:
        raise web.HTTPUnauthorized()
    
    user_id = None
    authenticator = Config.LP.AUTHENTICATION_PROCEDURE
    if not authenticator:
        raise ConfigError('LP.AUTHENTICATION_PROCEDURE is missing')
    try:
        user_id, role = await authenticator(token)
    except Exception as e:
        logger.exception('Authenticator error')
        raise e
    if not user_id:
        raise web.HTTPUnauthorized()
    return user_id, role
        
ASEXOR_SESSION = 'ASEXOR_SESSION'

async def middleware(app, handler):
    sessions = app.get(ASEXOR_SESSION)
    def retire(session_id):
            try:
                ses = sessions[session_id]
                ses.active = False
                del sessions[session_id]
                logger.debug('Session %s recycled', session_id)
            except KeyError:
                pass
    async def middleware_handler(request):
        if request.method == 'OPTIONS':
            return await handler(request)
        session_id = request.cookies.get(Config.LP.COOKIE_NAME)
        session = sessions.get(session_id) if session_id else None
        if session and time.time() - session.ts > Config.LP.MAX_SESSION_TIME:
            retire(session_id)
            session = None
            logger.debug('Session %s reached max life time', session_id)
        if not session:
            while True:
                session_id = base64.b85encode(os.urandom(32)).decode('ascii')
                if not session_id in sessions:
                    break
            
            user, role = await authenticate(request)    
            session = Session(user, role, 
                              app.loop.call_later(Config.LP.MAX_SESSION_INACTIVITY, retire, session_id),
                              loop =  app.loop)
            sessions[session_id] = session
            request['new_session'] = True
            logger.debug('Starting new session %s', session_id)
        else:
            session.retire_task.cancel()
            session.retire_task = app.loop.call_later(Config.LP.MAX_SESSION_INACTIVITY, retire, session_id)
            request['new_session'] = False
            logger.debug('Using existing session %s', session_id)
        request['initial_request'] = bool(request.headers.get('Authorization'))  
        request['session'] = session
            
            
        try:
            response = await handler(request)
            if not response.prepared:
                response.set_cookie(Config.LP.COOKIE_NAME, session_id, max_age = Config.LP.MAX_SESSION_TIME)
            return response
        except Exception:
            raise
        
    async def default_handler(request):
        return await handler(request)
    # use our middleware only for nonsystem handelrs
    if isinstance(handler, types.MethodType) and isinstance(handler.__self__, aiohttp.web_urldispatcher.SystemRoute ):
        return default_handler
    return middleware_handler

class CallContext(AbstractTaskContext):
    def __init__(self, call_id, session):
        self._session = session
        self.call_id = call_id
        
    def send(self, task_id, **kwargs):
        kwargs['task_id']=task_id
        self._session.add_message(UpdateMessage(self.call_id, kwargs).as_data())
            

class AsexorBackendSession(TaskSchedulerMixin):

    def __init__(self, tasks_queue, loop=None):
        self.tasks = tasks_queue
        self.loop = loop
        
    async def handle_call(self, request):
        if request.content_type != 'application/json':
            raise aiohttp.errors.HttpBadRequest()
        session = request['session']
        data=await request.text()
        logger.debug('Received message %s', data)
        
        async def handle_msg(data):
            try:
                call = CallMessage.from_json(data)
            except Exception as e:
                logger.exception('Invalid message %s', data)
                if hasattr(e, 'call_id'):
                    return ErrorMessage(e.call_id, str(e) or 'Invalid message')
                else:
                    return ErrorMessage(0, str(e) or 'Invalid message')
                
            ctx = CallContext(call.call_id, session)
            try:
                task_id = await self.schedule_task(
                    ctx, session.user, session.role, call.task_name, *call.args, **call.kwargs)
                res = ReplyMessage(call.call_id, task_id)
                logger.debug('Sending respose: %s', res)
                return res
            except Exception as e:
                error = str(e) or repr(e)
                tb = traceback.format_exc() if Config.SEND_REMOTE_ERROR_STACK else None
                logger.exception('Task scheduling error')
                return ErrorMessage(call.call_id, error, error_stack=tb)
            
        resp_message=await handle_msg(data)
        return web.json_response(resp_message.as_data())
    
    async def handle_messages(self, request):
        session = request['session']
        messages = []
        try:
            if not request['initial_request']: # for new or renewed session return immediately to provide session_id
                messages = await asyncio.wait_for(session.get_messages(),
                                              Config.LP.LONG_POLL_TIMEOUT,
                                              loop = request.app.loop)
            elif not request['new_session']:
                #There might be long polling request pending from previous interaction - release it
                session.release_wait()
        except asyncio.TimeoutError:
            pass
        
        return web.json_response(messages)
            
    

class LpAsexorBackend(AbstractHttpBackend):
    
    def create_app(self, tasks_queue):
        self.app = web.Application(loop=self.loop, middlewares=(middleware,))
        self.app[ASEXOR_SESSION] = dict()
        session = AsexorBackendSession(tasks_queue, loop=self.app.loop)
        
        
        res = self.app.router.add_resource('/')        
        route_get=res.add_route('POST', session.handle_call)
        route_post=res.add_route('GET', session.handle_messages)
        
        if Config.LP.ENABLE_CORS:
            
        
            cors = aiohttp_cors.setup(self.app, defaults={
                         Config.LP.CORS_ORIGIN : aiohttp_cors.ResourceOptions(
                                allow_credentials= Config.LP.CORS_ALLOW_CREDENTIAL,
                                expose_headers= Config.LP.CORS_EXPOSE_HEADERS,
                                allow_headers= Config.LP.CORS_ALLOW_HEADERS,
                            )
                    })
            cors.add(res)
            cors.add(route_get)
            cors.add(route_post)
        
        