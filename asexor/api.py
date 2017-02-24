import asyncio
import logging
from abc import ABC, abstractmethod, abstractproperty

logger = logging.getLogger('api')

class AbstractSessionAdapter(ABC):
    """
    Adapts backend session fro purpose of :class:`asexor.tqueue.TasksQueue`
    """

    @abstractmethod
    def notify_start(self, task_id, task_context=None):
        pass

    @abstractmethod
    def notify_success(self, task_id, res, duration, task_context=None):
        pass

    @abstractmethod
    def notify_progress(self, task_id, progress, task_context=None):
        pass

    @abstractmethod
    def notify_error(self, task_id, err, duration, task_context=None):
        pass


class AbstractRunner(ABC):
    """Class to run APEX backend process - implementation is specific for given protocol"""
    @abstractmethod
    def run(self, *, make=None, loop=None):
        """
        Runs ASEXOR backend, starts loops, waits for SIGTERM to stop

        :param make: (optional) factory to create backend specific session, based on backed type can require some params
        :param loop: (optional) asyncio event loop
        """
        pass
    

class AbstractClient(ABC):
    """
    Base class for ASEXOR Client Session
    
    Typically start client as:
    loop.run_until_complete(client.start())
    and then run client logging further in the loop
    """
    def __init__(self, loop=None):
        self._listeners = set()
        self._task = None
        self.loop = loop or asyncio.get_event_loop()
        self._ready = self.loop.create_future()
        
    def set_ready(self):
        self._ready.set_result(True)
        
    async def update_listeners(self, **data):
        for fn in self._listeners:
            try:
                await fn(**data)
            except Exception as e:
                logger.exception('Error when processing task update notification')
        
    async def start(self):
        self._task = self.loop.create_task(self.run())
        await self._ready
        
    async def stop(self):
        if not self._task:
            return
        self._task.cancel()
        try:
            await asyncio.wait_for(self._task, 5)
        except asyncio.CancelledError:
            pass
        except asyncio.TimeoutError:
            logger.warn('Session stop timeout')
        
    def subscribe(self, handler):
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError('Handler must be a coroutine function (async def)')
        self._listeners.add(handler)
        
    def unsubscribe(self, handler):
        try:
            self._listeners.remove(handler)
        except KeyError:
            pass
        
    def unsubscibe_all(self):
        self._listeners.clear()
        
        
    @abstractmethod
    def execute(self, remote_name, *args, **kwargs):
        pass
    
    @abstractmethod
    async def run(self):
        pass
    
    @abstractproperty
    def active(self):
        pass
        
    
