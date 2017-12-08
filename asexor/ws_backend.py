import asyncio
import logging
from collections import defaultdict
from aiohttp import web
import aiohttp
import traceback
from copy import copy
from collections import namedtuple

from asexor.api import AbstractTaskContext, AbstractHttpBackend
from asexor.config import Config, ConfigError
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from asexor.utils import asure_coro_fn
from asexor.tqueue import TaskSchedulerMixin

logger = logging.getLogger('ws_backend')


class CallContext(AbstractTaskContext):

    def __init__(self, call_id, user, session_id, sessions):
        self._sessions = sessions
        self.call_id = call_id
        self.user = user
        self.session_id = session_id

    def send(self, task_id, **kwargs):
        ws = self._sessions.get(self.user, self.session_id)
        kwargs['task_id']=task_id
        msg = UpdateMessage(self.call_id, kwargs).as_json()
        if not ws:
            logger.warn("WS sesssion user: %s id: %s expired - saving messages", self.user,self.session_id)
            self._sessions.add_to_unsent(msg, self.user, self.session_id)
            return
        try:
            ws.send_str(msg)
        except Exception:
            logger.exception('WS send failed')
        self._sessions.reset_timeout(self.user, self.session_id)
            
class Session:
    __slots__ = ('ws', 'handle', 'timeout')
    def __init__(self, ws, handle, timeout=None):
        self.ws = ws
        self.handle = handle
        self.timeout = timeout
        
    def update_timeout(self, to):
        if self.timeout: 
            self.timeout.cancel()
        self.timeout = to
        
        
class SessionsMap():
    def __init__(self, loop):
        self.loop = loop
        self._sessions = defaultdict(dict)
        self._unsent = defaultdict(dict)
        
    async def cancel_existing(self, user, session_id):
        if user in self._sessions and session_id in self._sessions[user]:
            logger.debug("Cancelling session user: %s, id: %s", user, session_id)
            session = self._sessions[user][session_id]
            session.handle.cancel()
            await session.ws.close(code=aiohttp.WSCloseCode.OK, message="Closing session %s replaced or timeout"%session_id)
            
    def get(self, user, session_id):
        try:
            return self._sessions[user][session_id].ws
        except KeyError:
            return None
        
    def add_to_unsent(self, msg, user, session_id):
        if user in self._unsent and session_id in self._unsent[user]:
            self._unsent[user][session_id].append(msg)
        else:
            def rm(user, session_id):
                if user in self._unsent and session_id in self._unsent[user]:
                    logger.warn("Removing unsent mesages for user: %s session id: %s", user, session_id)
                    del self._unsent[user][session_id]
                    if not self._unsent[user]:
                        del self._unsent[user]
            h = self.loop.call_later(Config.WS.UNSENT_MSG_TIMEOUT, rm, user, session_id)
            self._unsent[user][session_id]=[h,msg]
            
            
    def send_unsent(self,user, session_id):
        if user in self._unsent and session_id in self._unsent[user]:
            unsent = self._unsent[user][session_id]
            del self._unsent[user][session_id]
            h = unsent[0]
            h.cancel()
            ws = self._sessions[user][session_id].ws
            for m in unsent[1:]:
                ws.send_str(m)
        
            
    def add(self, ws, user, session_id):
        session=Session(ws, asyncio.Task.current_task())
        self._sessions[user][session_id] = session
        self.reset_timeout(user, session_id)
        
    def reset_timeout(self, user, session_id):
        if Config.WS.INACTIVE_TIMEOUT:
            timeout = self.loop.call_later(Config.WS.INACTIVE_TIMEOUT, 
                                 lambda u, sid: self.loop.create_task(self.cancel_existing(u, sid)), 
                                 user, session_id)
            if user in self._sessions and session_id in self._sessions[user]:
                self._sessions[user][session_id].update_timeout(timeout)
    
    def remove(self, user, session_id):
        timeout = self._sessions[user][session_id].timeout
        if timeout:
            timeout.cancel()
        del self._sessions[user][session_id]
        if not self._sessions[user]:
            del self._sessions[user]
            
    async def close_all(self, code, message):
        # here we have to be careful as self.websockets can be modified during iteration, because 
        #  closing we can remote it from here asynchronously
        # As it is just final cleanup we can allow overhead of copying data
        users = copy(self._sessions)
        for user in users:
            if not user in self._sessions:
                continue
            active_ws = copy(self._sessions[user])
            for _,s in active_ws.items():
                await s.ws.close(code=code,
                               message=message)
        self._sessions.clear()
        self._unsent.clear()

    
class AsexorBackendSession(TaskSchedulerMixin):

    def __init__(self, tasks_queue, loop):
        if not Config.WS.AUTHENTICATION_PROCEDURE:
            raise ConfigError('WS.AUTHENTICATION_PROCEDURE is missing')
        self.autheticator = asure_coro_fn(Config.WS.AUTHENTICATION_PROCEDURE)
        self.sessions = SessionsMap(loop)
        self.tasks = tasks_queue
        self.loop = loop

    def close_user_websockets(self, user):
        for handler in self.handlers[user]:
            handler.cancel()

    async def authenticate(self, request):
        token = request.rel_url.query.get('token')
        if not token:
            raise web.HTTPUnauthorized()
        else:
            user_id = None
            try:
                user_id, role = await self.autheticator(token)
            except Exception as e:
                logger.exception('Authenticator error')
                raise e
            if not user_id:
                raise web.HTTPUnauthorized()
            return user_id, role

    async def ws_handler(self, request):
        user, role = await self.authenticate(request)
        session_id = request.rel_url.query.get('session_id')
        ws = web.WebSocketResponse(heartbeat=Config.WS.HEARTBEAT)
        if not session_id:
            session_id = id(ws)
        await ws.prepare(request)
        await self.sessions.cancel_existing(user, session_id)
        self.sessions.add(ws, user, session_id)
        self.sessions.send_unsent(user, session_id)
        logger.debug("WS connected with session_id=%s", session_id)

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    logger.debug('Received message %s', msg.data)
                    try:
                        call = CallMessage.from_json(msg.data)
                    except Exception as e:
                        if hasattr(e, 'call_id'):
                            ws.send_str(ErrorMessage(e.call_id, str(e) or 'Invalid message').as_json())
                        logger.exception('Invalid message %s', msg.data)
                        continue
                    ctx = CallContext(call.call_id, user, session_id, self.sessions)
                    try:
                        task_id = await self.schedule_task(
                            ctx, user, role, call.task_name, *call.args, **call.kwargs)
                        res = ReplyMessage(call.call_id, task_id)
                        logger.debug('Sending respose: %s', res)
                        ws.send_str(res.as_json())
                        self.sessions.reset_timeout(user, session_id)
                    except Exception as e:
                        error = str(e) or repr(e)
                        tb = traceback.format_exc() if Config.SEND_REMOTE_ERROR_STACK else None
                        logger.exception('Task scheduling error')
                        ws.send_str(ErrorMessage(call.call_id, error, error_stack=tb).as_json())
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error('ws connection closed with exception %s' %
                                 ws.exception())
            logger.debug('websocket connection closed')
        except asyncio.CancelledError:
            logger.info('WebSocket for user %s was canceled', user)
        finally:
            self.sessions.remove(user, session_id)
        return ws

    async def close_all_websockets(self, *args, **kwargs):
        code = kwargs.get('code', aiohttp.WSCloseCode.SERVICE_RESTART)
        message = kwargs.get('message', 'Server shutdown')
        await self.sessions.close_all(code, message)
                
                
class WsAsexorBackend(AbstractHttpBackend):
    
    def __init__(self, loop, *, host='0.0.0.0', port=8484, 
        ssl_context=None, backlog=128, static_dir=None):
        AbstractHttpBackend.__init__(self, loop, host=host, port=port, ssl_context=ssl_context, backlog=backlog)
        self.static_dir = static_dir
        
    def create_app(self, tasks_queue): 
        self.app = web.Application(loop=self.loop)
        session = AsexorBackendSession(tasks_queue, self.app.loop)
        self.app.on_shutdown.append(session.close_all_websockets)
        
        self.app.router.add_get('/ws', session.ws_handler)
        if self.static_dir:
            self.app.router.add_static('/', self.static_dir, show_index=True, follow_symlinks=True)
            logger.info('Serving static  files from %s', self.static_dir)
           
    
    