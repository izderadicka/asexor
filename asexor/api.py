import asyncio
import logging
from abc import ABC, abstractmethod, abstractproperty

logger = logging.getLogger('api')

class AbstractTaskContext(ABC):
    """
    Adapts backend session fro purpose of :class:`asexor.tqueue.TasksQueue`
    """
    
    @abstractmethod
    def send(self, task_id, **kwargs):
        pass

    def notify_start(self, task_id,):
        self.send(task_id, status='started')

    def notify_success(self, task_id, res, duration):
        self.send(task_id, status='success', result=res, duration=duration)
        
    def notify_progress(self, task_id, progress):
        self.send(task_id, status='progress', progress=progress)

    def notify_error(self, task_id, err, duration):
        self.send(task_id, status='error', error=str(err) or repr(err), duration=duration)


class AbstractBackend(ABC):
    """Class to  run APEX backend protocol - implementation is specific for given protocol"""
    def __init__(self, loop, **kwargs):
        self.loop = loop
        
    @abstractmethod
    async def start(self, tasks_queue):
        """
        Starts backend protocol
        :param tasks_queue:  ASEXOR tasks queue 
        :type tasks_queue: `asexor.tqueue.TasksQueue`
        """
        pass
    
    @abstractmethod
    async def stop(self):
        """
        Stops backend protocol
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
        
    
