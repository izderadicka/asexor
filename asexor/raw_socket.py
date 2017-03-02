import asyncio
import struct
import logging

logger = logging.getLogger('raw_socket')

FRAME_TYPE_DATA = 0
FRAME_TYPE_PING = 1
FRAME_TYPE_PONG = 2

MAX_FRAME_SIZE = 16 # MB


class PrefixProtocol(asyncio.Protocol):

    prefix_format = '!L'
    prefix_length = struct.calcsize(prefix_format)
    max_length = MAX_FRAME_SIZE * 1024 * 1024
    max_length_send = max_length
    
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._wait_closed = self.loop.create_future()
   
    def connection_made(self, transport):
        self.transport = transport
        peer = transport.get_extra_info('peername')
        logger.debug('Connection made with peer %s',peer)
        self._buffer = b''
        self._header = None
        self.on_connected()
        
    def on_connected(self):
        pass

    async def wait_closed(self):
        await self._wait_closed

    def connection_lost(self, exc):
        logger.debug('Connection lost: %s', exc)
        self.transport = None
        self._wait_closed.set_result(True)
        self.on_disconnected(was_error=bool(exc))
        
    def on_disconnected(self, was_error):
        pass


    def protocol_error(self, msg):
        logger.error(msg)
        self.transport.close()

    def send(self, data, frame_type=0):
        
        l = len(data)
        if l > self.max_length_send:
            raise ValueError('Data too big')
        header = struct.pack(self.prefix_format, len(data))
        if frame_type:
            b = bytearray(header)
            b[0] = b[0] | frame_type
            header = bytes(b)
            header = header[0]
        self.transport.write(header)
        self.transport.write(data)

    def ping(self, data):
        raise NotImplementedError()

    def pong(self, data):
        raise NotImplementedError()

    def data_received(self, data):
        self._buffer += data
        pos = 0
        remaining = len(self._buffer)
        while remaining >= self.prefix_length:
            # do not recalculate header if available from previous call
            if self._header:
                frame_type, frame_length = self._header
            else:
                header = self._buffer[pos:pos + self.prefix_length]
                frame_type = ord(header[0:1]) & 0b00000111
                if frame_type > FRAME_TYPE_PONG:
                    self.protocol_error('Invalid frame type')
                    return
                frame_length = struct.unpack(self.prefix_format, b'\0' + header[1:])[0]
                if frame_length > self.max_length:
                    self.protocol_error('Frame too big')
                    return

            if remaining - self.prefix_length >= frame_length:
                self._header = None
                pos += self.prefix_length
                remaining -= self.prefix_length
                data = self._buffer[pos:pos + frame_length]
                pos += frame_length
                remaining -= frame_length

                if frame_type == FRAME_TYPE_DATA:
                    self.frame_received(data)
                elif frame_type == FRAME_TYPE_PING:
                    self.ping(data)
                elif frame_type == FRAME_TYPE_PONG:
                    self.pong(data)
            else:
                # save heaader
                self._header = frame_type, frame_length
                break

        self._buffer = self._buffer[:remaining]

    def frame_received(self, data):
        raise NotImplementedError()
