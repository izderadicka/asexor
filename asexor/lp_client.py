import aiohttp
import logging
import asyncio
try:
    import ujson as json
except ImportError:
    import json

logger = logging.getLogger('lp_client')

from asexor.api import AbstractClient, RemoteError
from asexor.message import CallMessage, msg_from_json, ReplyMessage, ErrorMessage

class LpAsexorClient(AbstractClient):
    def __init__(self,url, token, loop=None):
        super().__init__(loop)
        self._session = None
        self._running = True
        self._call_id = 1
        self.url = url
        self.token = token
        
        
    async def run(self):
        try:
            async with aiohttp.ClientSession(loop=self.loop) as self._session:
                first_call = True
                while self._running:
                    headers = {}
                    if first_call:
                        headers = {'Authorization': 'Bearer %s'% self.token}
                        
                        
                    async with self._session.get(self.url, headers=headers) as resp:
                        if resp.status != 200:
                            raise Exception('Long poll get status %d'% resp.status)
                        data = await resp.text()
                        data = json.loads(data)
                        assert isinstance(data, (list, tuple))
                        for msg_data in data:
                            self.update_listeners(**msg_data[2])
                    if first_call:
                        self.set_ready()
                    first_call = False
                    
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.exception('Long ppol loop error')
            raise e
        finally:
            self.set_closed()   
            
    async def execute(self, remote_name, *args, **kwargs):
        if not self.active:
            raise RuntimeError('Session is not active')
        msg = CallMessage(self._call_id, remote_name, args, kwargs)
        self._call_id+=1
        try:
            async with self._session.post(self.url, headers={'Content-type':'application/json'},
                                          data=msg.as_json()) as resp:
                data = await resp.text()
                response = msg_from_json(data)
                
                if isinstance(response, ReplyMessage):
                    return response.task_id
                elif isinstance(response, ErrorMessage):
                    raise RemoteError(response.error, response.error_stack)
        except:
            logger.exception("Error is execute")
            raise
            
        
        
    
    @property
    def active(self):
        return bool(self._session and not self._session.closed)
    
    def close(self):
        self._running = False
        if self._session:
            async def wait_closed():
                await self._session.close()
                #self.set_closed()
            self.loop.create_task(wait_closed())
        
                        
                                      
                
    
