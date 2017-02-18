import asyncio
import logging
from asexor.tqueue import TasksQueue, NORMAL_PRIORITY, AbstractSessionAdapter
from asexor.config import Config, ConfigError
from collections import defaultdict
from aiohttp import web
import aiohttp
import json
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


class SessionAdapter(AbstractSessionAdapter):

    def notify_start(self, task_id, task_context=None):
        task_context.send({'task_id': task_id,
                           'status': 'started'})

    def notify_success(self, task_id, res, duration, task_context=None):
        task_context.send({'task_id': task_id,
                           'status': 'success',
                           'result': res, 'duration': duration
                           })

    def notify_error(self, task_id, err, duration, task_context=None):
        task_context.send({'task_id': task_id,
                           'status': 'error',
                           'error': str(err) or repr(err),
                           'duration': duration,
                           })

    def notify_progress(self, task_id, progress, task_context=None):
        task_context.send({'task_id': task_id,
                           'status': 'progress',
                           'progress': progress,
                           })


class BackendSession:

    def __init__(self, loop=None):
        if not Config.WS_AUTHENTICATION_PROCEDUTE:
            raise ConfigError('WS_AUTHENTICATION_PROCEDUTE is missing')
        self.autheticator = assure_coro_fn(Config.WS_AUTHENTICATION_PROCEDUTE)
        self.websockets = defaultdict(set)
        self.handlers = defaultdict(set)
        self.tasks = TasksQueue(SessionAdapter(),
                                concurrent=Config.CONCURRENT_TASKS,
                                queue_size=Config.TASKS_QUEUE_MAX_SIZE)

    def start_tasks_queue(self, app):
        self._tq_task = app.loop.create_task(self.tasks.run_tasks())
        logger.debug('Tasks queue running in task %s', self._tq_task)

    async def stop_tasks_queue(self, *args, **kwargs):
        self.tasks.stop()
        if self._tq_task:
            self._tq_task.cancel()
            await self._tq_task

    class CallContext:

        def __init__(self, call_id, user, role,  ws, handler):
            self._ws = ws
            self._handler = handler
            self.call_id = call_id
            self.user = user
            self.role = role

        def send(self, data):
            self._ws.send_json(
                {'t': 'm', 'call_id': self.call_id, 'data': data})

        def close_session(self):
            self._handler.cancel()

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
                    data = msg.json()
                    call_id = data.get('call_id')
                    if not call_id:
                        logger.error('Message do not have call_id')
                        continue

                    def send_error(error):
                        ws.send_json(
                            {'t': 'e', 'call_id': call_id, 'error': error})
                    call_args = data.get('args', tuple())
                    if not isinstance(call_args, (list, tuple)):
                        send_error('args must be an array/list')
                        continue
                    if len(call_args) < 1:
                        send_error('task name argument is mandatory')
                        continue
                    task_name = call_args[0]
                    call_kwargs = data.get('kwargs', {})
                    if not isinstance(call_kwargs, dict):
                        send_error('kwargs must be a dict/object')
                        continue

                    ctx = BackendSession.CallContext(
                        call_id, user, role, ws, asyncio.Task.current_task())
                    try:
                        task_id = self.schedule_task(
                            ctx, task_name, *call_args[1:], **call_kwargs)
                        res = {
                            't': 'r', 'call_id': call_id, 'returned': task_id}
                        logger.debug('Sending respose: %s', res)
                        ws.send_json(res)
                    except Exception as e:
                        error = str(e)
                        tb = traceback.format_exc()
                        logger.exception('Task scheduling error')
                        ws.send_json(
                            {'t': 'e', 'call_id': call_id, 'error': error, 'error_stack_trace': tb})

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

    def schedule_task(self, ctx, task_name, *args, **kwargs):
        logger.debug(
            'Request for run task %s %s %s', task_name, args, kwargs)

        authid = ctx.user
        task_priority = Config.DEFAULT_PRIORITY
        if ctx.role:
            task_priority = Config.PRIORITY_MAP.get(
                ctx.role, Config.DEFAULT_PRIORITY)
        task_id = self.tasks.add_task(
            task_name, args, kwargs, task_priority, authenticated_user=authid,
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
