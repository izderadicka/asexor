import asyncio
import logging
from abc import ABC, abstractmethod, abstractproperty
from asexor.message import CallMessage, ErrorMessage, ReplyMessage, UpdateMessage
from asexor.config import Config

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
        self._closed = self.loop.create_future()
        self._started = False
        
        
    def set_ready(self, exc=None):
        try:
            if exc:
                self._ready.set_exception(exc)
            else:
                self._ready.set_result(True)
        except asyncio.InvalidStateError:
                logger.warn('ready future already resolved')
        
    def set_closed(self):
        self._closed.set_result(True)
    
    @abstractmethod    
    def close(self):
        pass
        
    async def wait_closed(self):
        if not self._started:
            return
        await self._closed
        
    async def update_listeners(self, **data):
        for fn in self._listeners:
            try:
                await fn(**data)
            except Exception as e:
                logger.exception('Error when processing task update notification')
        
    async def start(self):
        async def safe_run():
            try:
                await self.run()
            except Exception as e:
                self.set_ready(e)
                
        self._task = self.loop.create_task(safe_run())
        await self._ready
        self._started = True
        
    async def stop(self):
        try:
            self.close()
        except Exception as e:
            logger.error('Session close error: %s', e)
        else:
            try:
                await self.wait_closed()
            except:
                logger.exception('Client stop error')
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
        
class RemoteError(Exception):
    def __init__(self, msg, remote_stack_trace):
        self.message = msg
        self.remote_stack_trace = remote_stack_trace
        
    def __str__(self):
        return self.message +'\n' + self.remote_stack_trace    

class AbstractClientWithCallMatch(AbstractClient):
    """Client bases class that matches calls with responses"""
    
    def __init__(self, loop=None):
        AbstractClient.__init__(self, loop)
        self._call_id = 1
        self._pending_calls = dict()
        
    @property
    def _next_call_id(self):
        cid = self._call_id
        self._call_id+=1
        return cid

    @property    
    def active(self):
        return bool(self._ws and not self._ws.closed)
    
    @asyncio.coroutine  # It is coroutine - returns future       
    def execute(self, remote_name, *args, **kwargs):
        return self.execute_msg(CallMessage, remote_name, args, kwargs)
    
    @asyncio.coroutine
    def execute_msg(self, msg_cls, *args, **kwargs):
        if not self.active:
            raise RuntimeError('WebSocket is closed')
        call_id = self._next_call_id
        msg = msg_cls(call_id, *args, **kwargs)
        logger.debug('Message send: %s', msg)
        self.send_msg(msg)
        
        
        fut = self.loop.create_future()
        def timeout_future(call_id):
            if call_id in self._pending_calls:
                fut, _to = self._pending_calls.pop(call_id)
                fut.set_exception(TimeoutError('No response received'))
                
        to = self.loop.call_later(Config.CLIENT_CALL_TIMEOUT, timeout_future, call_id)
        self._pending_calls[call_id]=(fut, to)
        return fut
    
    @abstractmethod
    def send_msg(self, msg):
        pass
    
    def set_closed(self):
        AbstractClient.set_closed(self)
        for f,_t in self._pending_calls.values():
            f.cancel()
        
    
    # should be used n run method                
    async def process_msg(self, msg_data, deserializer):
        def get_call_future(resp): 
            try:
                fut,to = self._pending_calls.pop(resp.call_id)
                to.cancel()
                return fut
            except KeyError:
                logger.error('Unmached response %s', resp)
                
        try:
            response = deserializer(msg_data)
            logger.debug('Message received: %s', response)
        except Exception:
            logger.exception('Invalid message')
            return
        
        if isinstance(response, ReplyMessage):
            fut = get_call_future(response)
            if fut:
                fut.set_result(response.task_id)
        elif isinstance(response, ErrorMessage):
            fut = get_call_future(response)
            if fut:
                fut.set_exception(RemoteError(response.error, response.error_stack))
                
        elif isinstance(response,UpdateMessage):
            res = response.data
            assert('status' in res and 'task_id' in res)
            await self.update_listeners(**res)
        else:
            logger.error("Invalid message type")