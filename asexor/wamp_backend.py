import asyncio
import logging
import signal
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.types import PublishOptions, RegisterOptions
from asexor.api import AbstractTaskContext, AbstractBackend
from asexor.config import Config, ConfigError
from asexor.tqueue import TaskSchedulerMixin
from autobahn.asyncio.rawsocket import WampRawSocketClientFactory
from autobahn.wamp.types import ComponentConfig
from urllib.parse import urlparse

logger = logging.getLogger('wamp_backend')


class CallContext(AbstractTaskContext):

    def __init__(self, session, caller=None):
        self._session = session
        self._caller = caller
        if Config.WAMP.LIMIT_PUBLISH_BY == 'SESSION'  and self._caller:
            self._options = PublishOptions(eligible=[self._caller])
            # return PublishOptions(eligible_authid=[task_user]
        elif not Config.WAMP.LIMIT_PUBLISH_BY:
            self._options = None
        else:
            raise ConfigError('Invalid configuration for LIMIT_PUBLISH_BY')
        
    def send(self, task_id, **kwargs):
        kwargs['options'] = self._options
        try:
            self._session.publish(Config.WAMP.UPDATE_CHANNEL, task_id, **kwargs)
        except Exception:
            logger.exception('WAMP publish failed')
            

class AsexorBackendSession(ApplicationSession, TaskSchedulerMixin):
    
    def __init__(self, config, tasks_queue):
        super(AsexorBackendSession, self).__init__(config)
        self.tasks=tasks_queue

    async def onJoin(self, details):
        logger.info('started session with details %s', details)
        if Config.WAMP.AUTHENTICATION_PROCEDURE and Config.WAMP.AUTHENTICATION_PROCEDURE_NAME:
            self.register(Config.WAMP.AUTHENTICATION_PROCEDURE, Config.WAMP.AUTHENTICATION_PROCEDURE_NAME)
        if Config.WAMP.AUTHORIZATION_PROCEDURE and Config.WAMP.AUTHORIZATION_PROCEDURE_NAME:
            self.register(Config.WAMP.AUTHORIZATION_PROCEDURE, Config.WAMP.AUTHORIZATION_PROCEDURE_NAME)
            

        def run_task(task_name, *args, **kwargs):
            logger.debug(
                'Request for run task %s %s %s', task_name, args, kwargs)
            details = kwargs.pop('__call_details__', None)
            if not details:
                raise RuntimeError('Call details not available')
            role = details.caller_authrole
            user = details.caller_authid
            ctx = CallContext(self, details.caller)
            task_id = self.schedule_task(ctx, user, role, task_name, *args, **kwargs)
            return task_id
        self.register(run_task, Config.WAMP.RUN_TASK_PROC, RegisterOptions(
            details_arg='__call_details__'))


    def onDisconnect(self):
        logger.warn('Disconnected')
        
        

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


class WampAsexorBackend(AbstractBackend):
    """
    Runs WAMP backend session 
    """
    def __init__(self, loop, url, realm='realm1', extra=None, serializer=None):
        """
        :param url: either path on local server to unix socket (or unix:/path)
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
        self.loop=loop

    async def start(self, tasks_queue):
        
        # session factory
        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = AsexorBackendSession(cfg, tasks_queue)
            except Exception:
                logger.exception("App session could not be created! ")
                asyncio.get_event_loop().stop()
            else:
                return session

        _transport, self.protocol = await start_wamp_session(self.url, create, self.loop, self.serializer)
     
        
    async def stop(self):
        # give Goodbye message a chance to go through, if we still
        # have an active session
        # it's not working now - because protocol is_closed must return Future
        if self.protocol._session:
            await self.protocol._session.leave()
        
