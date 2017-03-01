from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.types import ComponentConfig
from asexor.wamp_backend import start_wamp_session
from asexor.config import Config
from asexor.api import AbstractClient
import logging

logger = logging.getLogger('wamp_client')


class WampAsexorClient(AbstractClient):
    
    class WampClientSession(ApplicationSession):

        def __init__(self,realm, user, token, update_handler, ready_cb):
            ApplicationSession.__init__(self, config=ComponentConfig(realm=realm))
            self.user = user
            self.token = token
            self._on_update = update_handler
            self._on_ready = ready_cb
    
        def onConnect(self):
            logger.debug('Connected')
            self.join(self.config.realm, [u"ticket"], self.user)
    
        def onChallenge(self, ch):
            if ch.method == 'ticket':
                logger.debug('Got challenge %s', ch)
                return self.token
            else:
                raise Exception('Invalid authentication method')
    
        async def onJoin(self,  details):
            logger.debug('Session joined %s', details)
    
            await self.subscribe(
                self.on_task_update, Config.WAMP.UPDATE_CHANNEL)
            
            if self._on_ready:
                self._on_ready()
    
        async def on_task_update(self, task_id, status=None, **kwargs):
            if self._on_update:
                await self._on_update(task_id=task_id, status=status, **kwargs)
    
        def onLeave(self, details):
            logger.debug("Leaving session %s", details)
            self.disconnect()
    
        def onDisconnect(self):
            logger.debug('Disconnected')
        
        
    def __init__(self, url, realm, user, token, loop=None):
        AbstractClient.__init__(self, loop)
        self.session = WampAsexorClient.WampClientSession(realm, user, token, 
                                                       self.update_listeners,
                                                       self.set_ready)
        self.url = url
        
    async def execute(self, task_name, *args, **kwargs):
        task_id = await self.session.call(Config.WAMP.RUN_TASK_PROC, task_name, *args, **kwargs)
        return task_id
    
            
    async def run(self):
        (t,p) = await start_wamp_session(self.url, lambda: self.session, self.loop)
        
    @property
    def active(self):
        return self.session.is_connected() and self.session.is_attached()
        