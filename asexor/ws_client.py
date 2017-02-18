import aiohttp
import asyncio
import logging

logger = logging.getLogger('ws_client')

class RemoteError(Exception):
    def __init__(self, msg, remote_stack_trace):
        self.message = msg
        self.remote_stack_trace = remote_stack_trace
        
    def __str__(self):
        return self.message +'\n' + self.remote_stack_trace

class AsexorClient:
    
    def __init__(self, url, token, loop=None):
        self._ws = None
        self._call_id = 1
        self._listeners = set()
        self._pending_calls = dict()
        self.url = url
        self.token = token
        self.loop = loop or asyncio.get_event_loop()
        self._ready = loop.create_future()
        self._task = None
        
    @property
    def _next_call_id(self):
        cid = self._call_id
        self._call_id+=1
        return cid
    
    async def wait_ready(self):
        await self._ready
        
    def start(self):
        self._task = self.loop.create_task(self.run())
        
    def stop(self):
        self._task.cancel()
        
    async def wait_finished(self):
        if not self._task:
            return
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        
    @property    
    def active(self):
        return bool(self._ws and not self._ws.closed)
    
    def subscribe(self, handler):
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError('Handler must be a coroutine function (async def)')
        self._listeners.add(handler)
        
    def unsubscribe(self, handler):
        try:
            self._listeners.remove(handler)
        except KeyError:
            pass
        
    def unsubscibe_all(self):
        self._listeners.clear()
        
        
    def execute(self, remote_name, *args, **kwargs):
        if not self.active:
            raise RuntimeError('WebSocket is closed')
        call_id = self._next_call_id
        self._ws.send_json({'call_id': call_id, 'args': [remote_name]+list(args), 'kwargs': kwargs})
        
        fut = self.loop.create_future()
        self._pending_calls[call_id]=fut
        return fut
        
    async def run(self):
        def get_call_future(data): 
            try:
                fut = self._pending_calls.pop(data.get('call_id'))
                return fut
            except KeyError:
                logger.error('Unmached response %s', data)
                
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('%s?token=%s'% (self.url, self.token)) as self._ws:
                self._ready.set_result(True)
                async for msg in self._ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            data = msg.json()
                        except Exception:
                            logger.exception('Invalid message')
                            continue
                        if not data or not data['t']:
                            logger.error('Invalid message content')
                            continue
                        
                        msg_type = data['t']
                        if msg_type == 'r':
                            fut = get_call_future(data)
                            if fut:
                                fut.set_result(data.get('returned'))
                        elif msg_type == 'e':
                            fut = get_call_future(data)
                            if fut:
                                fut.set_exception(RemoteError(data.get('error'), data.get('error_stack_trace')))
                                
                        elif msg_type == 'm':
                            for fn in self._listeners:
                                try:
                                    await fn(**data.get('data'))
                                except Exception as e:
                                    logger.exception('Error when processing notification')
                        else:
                            logger.error("Invalid message type")
                            
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        logger.info('WebSocket closed %s %s', msg.data, msg.extra)
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error('WebSocket error %s %s', msg.data, msg.extra)
                        break