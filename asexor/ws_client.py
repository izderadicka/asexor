import aiohttp
import asyncio
import logging
from asexor.api import AbstractClient
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage, msg_from_json

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
        msg = CallMessage(call_id, remote_name, args, kwargs)
        logger.debug('Message send: %s', msg)
        self._ws.send_str(msg.as_json())
        
        fut = self.loop.create_future()
        self._pending_calls[call_id]=fut
        return fut
        
    async def run(self):
        def get_call_future(resp): 
            try:
                fut = self._pending_calls.pop(resp.call_id)
                return fut
            except KeyError:
                logger.error('Unmached response %s', resp)
                
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('%s?token=%s'% (self.url, self.token)) as self._ws:
                self.set_ready()
                async for msg in self._ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            response = msg_from_json(msg.data)
                            logger.debug('Message received: %s', response)
                        except Exception:
                            logger.exception('Invalid message')
                            continue
                        
                        if isinstance(response, ReplyMessage):
                            fut = get_call_future(response)
                            if fut:
                                fut.set_result(response.task_id)
                        elif isinstance(response, ErrorMessage):
                            fut = get_call_future(response)
                            if fut:
                                fut.set_exception(RemoteError(response.error, response.error_stack_trace))
                                
                        elif isinstance(response,UpdateMessage):
                            res = response.data
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