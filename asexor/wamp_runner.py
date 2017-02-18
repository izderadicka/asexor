import six
import asyncio
import signal
from six.moves.urllib.parse import urlparse
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.rawsocket import WampRawSocketClientFactory
import logging

# TODO - unify with previous class
class ApplicationRunnerRawSocket(object):
    """
    This class is a convenience tool mainly for development and quick hosting
    of WAMP application components.

    It can host a WAMP application component in a WAMP-over-WebSocket client
    connecting to a WAMP router.
    """
    log=logging.getLogger('runner')
    def __init__(self, url, realm, extra=None, serializer=None):
        """
        :param url: Raw socket unicode - either path on local server to unix socket (or unix:/path)
             or tcp://host:port for internet socket
        :type url: unicode

        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode

        :param extra: Optional extra configuration to forward to the application component.
        :type extra: dict

        :param serializer:  WAMP serializer to use (or None for default serializer).
        :type serializer: `autobahn.wamp.interfaces.ISerializer`
        """
        assert(type(url) == six.text_type)
        assert(type(realm) == six.text_type)
        assert(extra is None or type(extra) == dict)
        self.url = url
        self.realm = realm
        self.extra = extra or dict()
        self.serializer = serializer

    def run(self, make, logging_level='info'):
        """
        Run the application component.

        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable
        """

        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = make(cfg)
            except Exception:
                self.log.exception("App session could not be created! ")
                asyncio.get_event_loop().stop()
            else:
                return session

        parsed_url = urlparse(self.url)

        if parsed_url.scheme == 'tcp':
            is_unix = False
            if not parsed_url.hostname or not parsed_url.port:
                raise ValueError('Host and port is required in URL')
        elif parsed_url.scheme == 'unix' or parsed_url.scheme == '':
            is_unix = True
            if not parsed_url.path:
                raise ValueError('Path to unix socket must be in URL')

        transport_factory = WampRawSocketClientFactory(create, serializer=self.serializer)

        loop = asyncio.get_event_loop()
        logging.basicConfig(level=logging.DEBUG if logging_level == 'debug' else logging.INFO)
        if logging_level == 'debug':
            loop.set_debug(True)

        try:
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except NotImplementedError:
            # signals are not available on Windows
            pass

        def handle_error(loop, context):
            self.log.error('Application Error: %s', context)
            if 'exception' in context and context['exception']:
                import traceback
                e = context['exception']
                tb='\n'.join(traceback.format_tb(e.__traceback__)) if hasattr(e, '__traceback__') else ''
                logging.error('Exception : %s \n %s', repr(e), tb)
            loop.stop()

        loop.set_exception_handler(handle_error)
        
        try:
            if is_unix:
                coro = loop.create_unix_connection(transport_factory, parsed_url.path)
            else:
                coro = loop.create_connection(transport_factory, parsed_url.hostname, parsed_url.port)
            (_transport, protocol) = loop.run_until_complete(coro)
    
    
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            self.log.debug('Left main loop waiting for completion')
            # give Goodbye message a chance to go through, if we still
            # have an active session
            # it's not working now - because protocol is_closed must return Future
            if protocol._session:
                loop.run_until_complete(protocol._session.leave())
        finally:
            loop.close()
