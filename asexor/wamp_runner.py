import six
import asyncio
import signal
from six.moves.urllib.parse import urlparse
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.rawsocket import WampRawSocketClientFactory
from asexor.api import AbstractRunner
import logging


@asyncio.coroutine # is coroutine because returns coroutine
def start_wamp_session(url, session_factory, loop, serializer = None):
    parsed_url = urlparse(url)
    transport_factory = None
    if parsed_url.scheme == 'tcp':
        is_unix = False
        if not parsed_url.hostname or not parsed_url.port:
            raise ValueError('Host and port is required in URL')
        transport_factory = WampRawSocketClientFactory(session_factory, serializer=serializer)
    elif parsed_url.scheme == 'unix' or parsed_url.scheme == '':
        is_unix = True
        if not parsed_url.path:
            raise ValueError('Path to unix socket must be in URL')
        transport_factory = WampRawSocketClientFactory(session_factory, serializer=serializer)
        
    else:
        raise ValueError('Invalid URL scheme')

    if is_unix:
        coro = loop.create_unix_connection(transport_factory, parsed_url.path)
    else:
        coro = loop.create_connection(transport_factory, parsed_url.hostname, parsed_url.port)
    
    return coro

# TODO - unify with previous class
class ApplicationRunnerRawSocket(AbstractRunner):
    """
    Runs WAMP session (defined by ApplicationSession class) over raw socket protocol (eiher TCP socket,
    or UNIX domain socket).
    As WAMP is basically symmetrical can be used to run either ASEXOR backend or ASEXOR client.
    Runs forever until terminated by signal (TERM) or default asyncio loop is stopped.
    """
    log=logging.getLogger('wamp_runner')
    def __init__(self, url, realm='realm1', extra=None, serializer=None):
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
        
        # loop initialization
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
        
        
        # session factory
        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = make(cfg)
            except Exception:
                self.log.exception("App session could not be created! ")
                asyncio.get_event_loop().stop()
            else:
                return session

        coro = start_wamp_session(self.url, create, loop, self.serializer)
        (_transport, protocol) = loop.run_until_complete(coro)
        
        try:
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
