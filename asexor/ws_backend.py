import asyncio
import logging
from asexor.api import AbstractTaskContext, AbstractBackend
from asexor.config import Config, ConfigError
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from asexor.utils import asure_coro_fn
from asexor.tqueue import TaskSchedulerMixin
from collections import defaultdict
from aiohttp import web
import aiohttp
import traceback
from copy import copy

logger = logging.getLogger('ws_backend')


class CallContext(AbstractTaskContext):

    def __init__(self, call_id, ws):
        self._ws = ws
        self.call_id = call_id

    def send(self, task_id, **kwargs):
        kwargs['task_id']=task_id
        try:
            self._ws.send_str(UpdateMessage(self.call_id, kwargs).as_json())
        except Exception:
            logger.exception('WS send failed')


class AsexorBackendSession(TaskSchedulerMixin):

    def __init__(self, tasks_queue, loop=None):
        if not Config.WS.AUTHENTICATION_PROCEDURE:
            raise ConfigError('WS.AUTHENTICATION_PROCEDURE is missing')
        self.autheticator = asure_coro_fn(Config.WS.AUTHENTICATION_PROCEDURE)
        self.websockets = defaultdict(set)
        self.handlers = defaultdict(set)
        self.tasks = tasks_queue

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
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets[user].add(ws)
        self.handlers[user].add(asyncio.Task.current_task())

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
                    ctx = CallContext(call.call_id, ws)
                    try:
                        task_id = self.schedule_task(
                            ctx, user, role, call.task_name, *call.args, **call.kwargs)
                        res = ReplyMessage(call.call_id, task_id)
                        logger.debug('Sending respose: %s', res)
                        ws.send_str(res.as_json())
                    except Exception as e:
                        error = str(e) or repr(e)
                        tb = traceback.format_exc()
                        logger.exception('Task scheduling error')
                        ws.send_str(ErrorMessage(call.call_id, error, error_stack=tb).as_json())
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error('ws connection closed with exception %s' %
                                 ws.exception())
            logger.debug('websocket connection closed')
        except asyncio.CancelledError:
            logger.info('WebSocket for user %s was canceled', user)
        finally:
            self.websockets[user].remove(ws)
            self.handlers[user].remove(asyncio.Task.current_task())
        return ws

    async def close_all_websockets(self, *args, **kwargs):
        code = kwargs.get('code', aiohttp.WSCloseCode.SERVICE_RESTART)
        message = kwargs.get('message', 'Server shutdown')
        for user in self.websockets:
            active_ws = copy(self.websockets[user])
            for ws in active_ws:
                await ws.close(code=code,
                               message=message)
                
                
class WsAsexorBackend(AbstractBackend):
    
    def __init__(self, loop, host='0.0.0.0', port=8484, static_dir=None, 
                 ssl_context=None, backlog=128):
        """ Starts http server on host:post, serving ASEXOR protocol via WebSocketon http://host:port/ws.
        
        :param host: - interface to listen on, default is 0.0.0.0 - all available interfaces
        :param port: TCP post to listen on
        :param static_dir: - serve also files from this directory - only for test and development !
        """
        self.loop=loop
        self.host = host
        self.port = port
        self.static_dir = static_dir
        self.app = None
        self.ssl_context = ssl_context
        self.backlog = backlog
        
        
    
    async def start(self, tasks_queue):
        """
        Starts aiohttp server for ASEXOR WebSocket protocol
        """ 
        
        self.app = web.Application(loop=self.loop)
        session = AsexorBackendSession(tasks_queue, self.app.loop)
        self.app.on_shutdown.append(session.close_all_websockets)
        
        self.app.router.add_get('/ws', session.ws_handler)
        if self.static_dir:
            self.app.router.add_static('/', self.static_dir, show_index=True, follow_symlinks=True)
            logger.info('Serving static  files from %s', self.static_dir)
        
        
        self.handler = self.app.make_handler(access_log=aiohttp.log.access_logger)
    
        await self.app.startup()
        self.srv = await self.loop.create_server(self.handler, self.host,
                                                         self.port, ssl=self.ssl_context,
                                                         backlog=self.backlog)
    
        logger.info('aiohttp server running on %s port %s', self.host, self.port)
        
        
    async def stop(self):
        self.srv.close()
        await self.srv.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown(10.0)
        await self.app.cleanup()

