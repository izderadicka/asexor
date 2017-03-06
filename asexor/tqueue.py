import asyncio
import uuid
from collections import namedtuple
from asexor.task import get_task, BaseMultiTask, BaseSimpleTask
from multiprocessing import cpu_count
from asexor.config import NORMAL_PRIORITY, Config, ConfigError
import logging
import time

logger = logging.getLogger('tqueue')

TaskInfo = namedtuple(
    'TaskInfo', ['id', 'task', 'args', 'kwargs', 'context', 'multitask', 'task_no', 'total_tasks'])

class TaskSchedulerMixin:
    """
    To be used within classes that have self.tasks as instance of TasksQueue
    """
    
    async def schedule_task(self, ctx, user, role, task_name, *args, **kwargs):
        logger.debug(
            'Request for run task %s %s %s', task_name, args, kwargs)

        task_priority = Config.DEFAULT_PRIORITY
        if role:
            priority_map = Config.PRIORITY_MAP
            if asyncio.iscoroutinefunction(priority_map):
                task_priority = (await priority_map(role)) or Config.DEFAULT_PRIORITY
            elif isinstance(priority_map, dict):
                task_priority = Config.PRIORITY_MAP.get(
                    role, Config.DEFAULT_PRIORITY)
        
        auth_fn = Config.AUTHORIZATION_PROCEDURE        
        if  auth_fn and asyncio.iscoroutinefunction(auth_fn):
            if not (await auth_fn(task_name, role)):
                raise Exception("Not authorised to run %s" % task_name)
                
            
        task_id = self.tasks.add_task(
            task_name, args, kwargs, task_priority, authenticated_user=user,
            task_context=ctx)
        return task_id

class TasksQueue():

    def __init__(self, concurrent=None, queue_size=0):
        self._q = asyncio.PriorityQueue(maxsize=queue_size)
        self._running = True
        if not concurrent:
            concurrent = cpu_count()
        self._cc_semaphore = asyncio.Semaphore(concurrent)

    def add_task(self, task_name, task_args=(), task_kwargs={}, 
                 task_priority=NORMAL_PRIORITY, authenticated_user=None, task_context=None):
        assert(not task_context is None)
        task = get_task(task_name)(user=authenticated_user)
        task_id = uuid.uuid4().hex
        loop = asyncio.get_event_loop()
        #async def _add():
            # we need to assure that task_id from run_task is sent before first update
            # this is a hack - need to find a better way 
            # await asyncio.sleep(0.1)
            # for security reason consider sync version of put and throw error when q is full
#             await self._q.put((task_priority, time.time(), TaskInfo(task_id, task, task_args, task_kwargs, task_context, 
#                                                        None, None, None)))
        self._q.put_nowait((task_priority, time.time(), TaskInfo(task_id, task, task_args, task_kwargs, task_context, 
                                                       None, None, None)))
        return task_id
    
    async def add_subtask(self, multitask, task_no, total_tasks, task_name, task_args=(), task_kwargs={}, 
                 task_priority=NORMAL_PRIORITY, authenticated_user=None, task_context=None):
        assert(not task_context is None)
        task = get_task(task_name)(user=authenticated_user)
        task_id = uuid.uuid4().hex
        await self._q.put((task_priority, time.time(), TaskInfo(task_id, task, task_args, task_kwargs, task_context, 
                                                   multitask, task_no, total_tasks)))
           

    def stop(self):
        self._running = False

    async def join(self, initial_wait=None):
        if initial_wait:
            await asyncio.sleep(initial_wait)
        await self._q.join()

    async def run_tasks(self):
        logger.debug('Started tasks queue')
        try:
            while self._running:
                await self._cc_semaphore.acquire()
                priority, _ts, task = await self._q.get()
                logger.debug('Got task %s', task.id)
                if isinstance(task.task, BaseSimpleTask):
                    
                    if task.multitask:
                        self.run_async(self.run_subtask, task, (priority,))
                    else:
                        # notify task start
                        task.context.notify_start(task.id)
                        self.run_async(self.run_one, task)
                    
                elif isinstance(task.task, BaseMultiTask):
                    # notify task start
                    task.context.notify_start(task.id)
                    self.run_async(self.start_multitask, task, (priority,), 
                                   error_msg='Multitask %s(%s, %s) id %s start failed with %s')
        except asyncio.CancelledError:
            logger.info('Tasks queue terminated by cancel')
            raise
        except Exception:
            if self._running: #ignore exceptions when closing
                logger.exception('Tasks queue error')
                raise
            
    def run_async(self, fn, task, args=(), error_msg='Task %s(%s, %s) id %s failed with %s'):   
        async def _inner():
            try:
                await fn(task, *args)
            except Exception as e:
                logger.exception(error_msg,
                             task.task.NAME, task.args, task.kwargs, task.id, e)
                task.context.notify_error(task.id, e, task.task.duration)
            finally:
                    self._q.task_done()
                    self._cc_semaphore.release()
        asyncio.ensure_future(_inner())
                  

    async def start_multitask(self, task, priority):
        def multitask_finished(res):
            task.context.notify_success(task.id, res, task.task.duration)
        await task.task.start(*task.args, **task.kwargs)
        new_task = await task.task.next_task()
        if not new_task:
            await task.task.update_task_result(None, result=None, 
                                                         on_all_finished=multitask_finished)
            
        else:
            await self.add_subtask(task, new_task.task_no, new_task.total_tasks, new_task.task_name, 
                               new_task.task_args, new_task.task_kwargs, priority, task.task.user,
                               task.context)
        
        
    
    async def run_one(self, task):
        res = await task.task.run(*task.args, **task.kwargs)
        task.context.notify_success(task.id, res, task.task.duration)
        
    async def run_subtask(self, task, priority):
        def multitask_finished(res):
            task.multitask.context.notify_success(task.multitask.id, res, task.multitask.task.duration)
            
        def multitask_progress(progress):
            task.multitask.context.notify_progress(task.multitask.id, progress)
        try:
            res = await task.task.run(*task.args, **task.kwargs)
            await task.multitask.task.update_task_result(task.task_no, result=res, 
                                                         on_all_finished=multitask_finished,
                                                         on_progress=multitask_progress)
        except Exception as e:
            logger.warn('Subtask %d error %s', task.task_no, e)
            try:
                await task.multitask.task.update_task_result(task.task_no, error=e, 
                                                         on_all_finished=multitask_finished,
                                                         on_progress=multitask_progress)
            except Exception as e:
                logger.exception('Task update error')
                task.multitask.context.notify_error(task.multitask.id, e, task.multitask.task.duration)
                return
        try:
            new_task = await task.multitask.task.next_task()
            if new_task:
                await self.add_subtask(task.multitask, new_task.task_no, new_task.total_tasks, new_task.task_name, 
                                       new_task.task_args, new_task.task_kwargs, priority, 
                                       task.task.user, task.context)
        except Exception as e:
            logger.exception('Get next task error')
            task.multitask.context.notify_error(task.multitask.id, e, task.multitask.task.duration)
            
            
            
   
        
