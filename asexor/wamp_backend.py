import asyncio
import logging
import signal
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.types import PublishOptions, RegisterOptions
from asexor.tqueue import TasksQueue, NORMAL_PRIORITY
from asexor.api import AbstractTaskContext, AbstractRunner
from asexor.config import Config, ConfigError
from autobahn.asyncio.rawsocket import WampRawSocketClientFactory
from autobahn.wamp.types import ComponentConfig
from urllib.parse import urlparse

log = logging.getLogger('wamp_backend')


class CallContext(AbstractTaskContext):

    def __init__(self, session, caller=None):
        self._session = session
        self._caller = caller

    def _options(self):
        if Config.LIMIT_PUBLISH_BY == 'SESSION'  and self._caller:
            return PublishOptions(eligible=[self._caller])
        elif not Config.LIMIT_PUBLISH_BY:
            return None

        raise ConfigError('Invalid configuration for LIMIT_PUBLISH_BY')

        # return PublishOptions(eligible_authid=[task_user]

    def notify_start(self, task_id,):
        self._session.publish(Config.UPDATE_CHANNEL, task_id, status='started',
                              options=self._options())

    def notify_success(self, task_id, res, duration):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='success', result=res, duration=duration,
                              options=self._options())
        
    def notify_progress(self, task_id, progress):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='progress', progress=progress,
                              options=self._options())

    def notify_error(self, task_id, err, duration):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='error', error=str(err) or repr(err), duration=duration,
                              options=self._options())


class WampAsexorBackend(ApplicationSession):

    async def onJoin(self, details):
        log.info('started session with details %s', details)
        if Config.AUTHENTICATION_PROCEDUTE and Config.AUTHENTICATION_PROCEDURE_NAME:
            self.register(Config.AUTHENTICATION_PROCEDUTE, Config.AUTHENTICATION_PROCEDURE_NAME)
        if Config.AUTHORIZATION_PROCEDURE and Config.AUTHORIZATION_PROCEDURE_NAME:
            self.register(Config.AUTHORIZATION_PROCEDURE, Config.AUTHORIZATION_PROCEDURE_NAME)
            
        self.tasks = TasksQueue(concurrent=Config.CONCURRENT_TASKS,
                                queue_size=Config.TASKS_QUEUE_MAX_SIZE)

        def run_task(task_name, *args, **kwargs):
            log.debug(
                'Request for run task %s %s %s', task_name, args, kwargs)
            details = kwargs.pop('__call_details__', None)
            if not details:
                raise RuntimeError('Call details not available')
            role = details.caller_authrole
            authid = details.caller_authid
            task_priority = Config.DEFAULT_PRIORITY
            if role:
                task_priority = Config.PRIORITY_MAP.get(
                    role, Config.DEFAULT_PRIORITY)
            task_id = self.tasks.add_task(
                task_name, args, kwargs, task_priority, authenticated_user=authid, 
                task_context=CallContext(self, details.caller))
            return task_id
        self.register(run_task, Config.RUN_TASK_PROC, RegisterOptions(
            details_arg='__call_details__'))

        try:
            await self.tasks.run_tasks()
        except Exception as e:
            # ignore exception caused by closing loop
            if not asyncio.get_event_loop().is_closed():
                log.exception(e)

    def onDisconnect(self):
        log.warn('Disconnected')
        #TODO: is below needed?
        asyncio.get_event_loop().stop()
        

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


class WampBackendRunner(AbstractRunner):
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
        assert(type(url) == str)
        assert(type(realm) == str)
        assert(extra is None or type(extra) == dict)
        self.url = url
        self.realm = realm
        self.extra = extra or dict()
        self.serializer = serializer

    def run(self, *, make=WampAsexorBackend, loop=None):
        """
        Run the application component.

        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable or class
        """
        
        # loop initialization
        loop = loop or asyncio.get_event_loop()
        

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
