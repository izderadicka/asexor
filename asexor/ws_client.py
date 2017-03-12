import aiohttp
import logging
from asexor.api import AbstractClientWithCallMatch
from asexor.message import msg_from_json
import asyncio

logger = logging.getLogger('ws_client')


class AsexorClient(AbstractClientWithCallMatch):
    
    def __init__(self, url, token, loop=None):
        AbstractClientWithCallMatch.__init__(self, loop)
        self._ws = None
        self.url = url
        self.token = token
        
    
    @property    
    def active(self):
        return bool(self._ws and not self._ws.closed)
    
    
    def send_msg(self, msg):
        self._ws.send_str(msg.as_json())
        
    async def run(self):
        try:
            async with aiohttp.ClientSession(loop=self.loop) as session:
                async with session.ws_connect('%s?token=%s'% (self.url, self.token)) as self._ws:
                    self.set_ready()
                    async for msg in self._ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self.process_msg(msg.data, msg_from_json)
                                
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            logger.info('WebSocket closed %s %s', msg.data, msg.extra)
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error('WebSocket error %s %s', msg.data, msg.extra)
                            break
        finally:
            self.set_closed()
                    
    def close(self):
        if self._ws:
            async def wait_closed():
                await self._ws.close()
                #self.set_closed()
            self.loop.create_task(wait_closed())