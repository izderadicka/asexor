import aiohttp
import asyncio
import logging
from asexor.api import AbstractClient

logger = logging.getLogger('ws_client')

class RemoteError(Exception):
    def __init__(self, msg, remote_stack_trace):
        self.message = msg
        self.remote_stack_trace = remote_stack_trace
        
    def __str__(self):
        return self.message +'\n' + self.remote_stack_trace

class AsexorClient(AbstractClient):
    
    def __init__(self, url, token, loop=None):
        AbstractClient.__init__(self, loop)
        self._ws = None
        self._call_id = 1
        self._pending_calls = dict()
        self.url = url
        self.token = token
        
    @property
    def _next_call_id(self):
        cid = self._call_id
        self._call_id+=1
        return cid

    @property    
    def active(self):
        return bool(self._ws and not self._ws.closed)
    
    @asyncio.coroutine  # It is coroutine - returns future       
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
                self.set_ready()
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
                            res = data.get('data')
                            assert('status' in res and 'task_id' in res)
                            await self.update_listeners(**res)
                        else:
                            logger.error("Invalid message type")
                            
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        logger.info('WebSocket closed %s %s', msg.data, msg.extra)
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error('WebSocket error %s %s', msg.data, msg.extra)
                        break