import asyncio
import logging
from asexor.api import AbstractTaskContext, AbstractBackend
from asexor.config import Config, ConfigError
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from collections import defaultdict
from aiohttp import web
import aiohttp
import traceback
from copy import copy

logger = logging.getLogger('ws_backend')


def assure_coro_fn(fn_or_coro):
    if asyncio.iscoroutinefunction(fn_or_coro):
        return fn_or_coro
    elif callable(fn_or_coro):
        return asyncio.coroutine(fn_or_coro)
    else:
        raise ValueError('Parameter is not method, function or coroutine')

class CallContext(AbstractTaskContext):

    def __init__(self, call_id, ws):
        self._ws = ws
        self.call_id = call_id

    def _send(self, data):
        self._ws.send_str(UpdateMessage(self.call_id, data).as_json())


    def notify_start(self, task_id):
        self._send({'task_id': task_id,
                           'status': 'started'})

    def notify_success(self, task_id, res, duration):
        self._send({'task_id': task_id,
                           'status': 'success',
                           'result': res, 'duration': duration
                           })

    def notify_error(self, task_id, err, duration):
        self._send({'task_id': task_id,
                           'status': 'error',
                           'error': str(err) or repr(err),
                           'duration': duration,
                           })

    def notify_progress(self, task_id, progress, task_context=None):
        self._send({'task_id': task_id,
                           'status': 'progress',
                           'progress': progress,
                           })


class AsexorBackendSession:

    def __init__(self, tasks_queue, loop=None):
        if not Config.WS_AUTHENTICATION_PROCEDUTE:
            raise ConfigError('WS_AUTHENTICATION_PROCEDUTE is missing')
        self.autheticator = assure_coro_fn(Config.WS_AUTHENTICATION_PROCEDUTE)
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
                        error = str(e)
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

    def schedule_task(self, ctx, user, role, task_name, *args, **kwargs):
        logger.debug(
            'Request for run task %s %s %s', task_name, args, kwargs)

        task_priority = Config.DEFAULT_PRIORITY
        if role:
            task_priority = Config.PRIORITY_MAP.get(
                role, Config.DEFAULT_PRIORITY)
        task_id = self.tasks.add_task(
            task_name, args, kwargs, task_priority, authenticated_user=user,
            task_context=ctx)
        return task_id

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

