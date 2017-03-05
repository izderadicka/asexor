import asyncio
from asexor.api import AbstractClientWithCallMatch
from asexor.raw_socket import PrefixProtocol
from asexor.message import msg_from_binary, DelegatedCallMessage
import logging
from urllib.parse import urlparse
from inspect import CORO_CLOSED

logger = logging.getLogger('raw_client')


class RawSocketAsexorClient(AbstractClientWithCallMatch):
    
    class ClientSession(PrefixProtocol):
        
        def __init__(self, token, msg_handler, on_ready, on_closed=None, loop=None):
            PrefixProtocol.__init__(self, loop=loop)
            self.token = token if isinstance(token, bytes) else token.encode('utf-8')
            self._msg_handler = msg_handler
            self._hs_done = False
            self._on_ready = on_ready
            self._on_closed = on_closed
            
        def on_connected(self):
            logger.debug('Transport buffer: %s', self.transport.get_write_buffer_limits())
            self.send(self.token)
            
        def on_disconnected(self, was_error):
            if self._on_closed:
                self._on_closed()
            
        def frame_received(self, data):
            if self._hs_done:
                self.loop.create_task(self._msg_handler(data, msg_from_binary))
            else:
                if data == b'\x00':
                    self._hs_done = True
                    logger.debug('Handshake complete')
                    self._on_ready()
                else:
                    self.protocol_error('Hadshake failure, code: %s'% data)
                    
            
        
    
    def __init__(self, url, token, loop=None):
        AbstractClientWithCallMatch.__init__(self, loop)
        self._ws = None
        self.url = url
        self.token = token
        self._session = None
    
    @property    
    def active(self):
        return bool(self._session and self._session.transport)
    
    def close(self):
        self._session.close()
    
    
    def send_msg(self, msg):
        self._session.send(msg.as_binary())
        
    async def run(self):
        self._session = RawSocketAsexorClient.ClientSession(self.token, self.process_msg, 
                                                            on_ready=self.set_ready, 
                                                            on_closed=self.set_closed,
                                                            loop=self.loop)
        parsed_url = urlparse(self.url)
        fact = lambda: self._session
        if parsed_url.scheme =='tcp':
            coro=self.loop.create_connection(fact,
                                    host=parsed_url.hostname, port=parsed_url.port)
        elif parsed_url.scheme =='unix' or parsed_url.scheme == '':
            coro = self.loop.create_unix_connection(fact, path= parsed_url.path)
            
        self.transport, _p = await coro
        
        #await self._session.wait_closed()
            

class DelegatedRawSocketAsexorClient(RawSocketAsexorClient):    
    
    @asyncio.coroutine
    def execute(self, user, role, remote_name, *args, **kwargs):
        if not self.active:
            raise RuntimeError('WebSocket is closed')
        call_id = self._next_call_id
        msg = DelegatedCallMessage(call_id, remote_name, args, kwargs,user,role)
        logger.debug('Message send: %s', msg)
        self.send_msg(msg)
        
        fut = self.loop.create_future()
        self._pending_calls[call_id]=fut
        return fut
            