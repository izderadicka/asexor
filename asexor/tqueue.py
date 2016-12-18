import asyncio
import uuid
from collections import namedtuple
from asexor.task import get_task, BaseMultiTask, BaseSimpleTask
from multiprocessing import cpu_count
from asexor.config import NORMAL_PRIORITY
import logging

logger = logging.getLogger('tqueue')

TaskInfo = namedtuple(
    'TaskInfo', ['id', 'task', 'args', 'kwargs', 'user', 'multitask', 'task_no', 'total_tasks'])


class TasksQueue():

    def __init__(self, session, concurrent=None, queue_size=0):
        self._q = asyncio.PriorityQueue(maxsize=queue_size)
        self._session = session
        self._running = True
        if not concurrent:
            concurrent = cpu_count()
        self._cc_semaphore = asyncio.Semaphore(concurrent)

    def add_task(self, task_name, task_user, task_args=(), task_kwargs={}, 
                 task_priority=NORMAL_PRIORITY, authenticated_user=None):
        task = get_task(task_name)(user=authenticated_user)
        task_id = uuid.uuid4().hex
        loop = asyncio.get_event_loop()
        async def _add():
            # we need to assure that task_id from run_task is sent before first update
            # this is a hack - need to find a better way 
            await asyncio.sleep(0.1)
            # for security reason consider sync version of put and throw error when q is full
            await self._q.put((task_priority, TaskInfo(task_id, task, task_args, task_kwargs, task_user, 
                                                       None, None, None)))
        loop.create_task(_add())
        return task_id
    
    async def add_subtask(self, multitask, task_no, total_tasks, task_name, task_user, task_args=(), task_kwargs={}, 
                 task_priority=NORMAL_PRIORITY, authenticated_user=None):
        task = get_task(task_name)(user=authenticated_user)
        task_id = uuid.uuid4().hex
        await self._q.put((task_priority, TaskInfo(task_id, task, task_args, task_kwargs, task_user, 
                                                   multitask, task_no, total_tasks)))
           

    def stop(self):
        self._running = False

    async def join(self, initial_wait=None):
        if initial_wait:
            await asyncio.sleep(initial_wait)
        await self._q.join()

    async def run_tasks(self):
        while self._running:
            await self._cc_semaphore.acquire()
            priority, task = await self._q.get()
            if isinstance(task.task, BaseSimpleTask):
                
                if task.multitask:
                    self.run_async(self.run_subtask, task, (priority,))
                else:
                    # notify task start
                    self._session.notify_start(task.id, task.user)
                    self.run_async(self.run_one, task)
                
            elif isinstance(task.task, BaseMultiTask):
                # notify task start
                self._session.notify_start(task.id, task.user)
                self.run_async(self.start_multitask, task, (priority,), 
                               error_msg='Multitask %s(%s, %s) id %s start failed with %s')
            
    def run_async(self, fn, task, args=(), error_msg='Task %s(%s, %s) id %s failed with %s'):   
        async def _inner():
            try:
                await fn(task, *args)
            except Exception as e:
                logger.exception(error_msg,
                             task.task.NAME, task.args, task.kwargs, task.id, e)
                self._session.notify_error(task.id, task.user, e, task.task.duration)
            finally:
                    self._q.task_done()
                    self._cc_semaphore.release()
        asyncio.ensure_future(_inner())
                  

    async def start_multitask(self, task, priority):
        def multitask_finished(res):
            self._session.notify_success(task.id, task.user, res, task.task.duration)
        await task.task.start(*task.args, **task.kwargs)
        new_task = await task.task.next_task()
        if not new_task:
            await task.task.update_task_result(None, result=None, 
                                                         on_all_finished=multitask_finished)
            
        else:
            await self.add_subtask(task, new_task.task_no, new_task.total_tasks, new_task.task_name, task.user, 
                               new_task.task_args, new_task.task_kwargs, priority, task.task.user)
        
        
    
    async def run_one(self, task):
        res = await task.task.run(*task.args, **task.kwargs)
        self._session.notify_success(task.id, task.user, res, task.task.duration)
        
    async def run_subtask(self, task, priority):
        def multitask_finished(res):
            self._session.notify_success(task.multitask.id, task.multitask.user, res, task.multitask.task.duration)
            
        def multitask_progress(progress):
            self._session.notify_progress(task.multitask.id, task.multitask.user, progress)
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
                self._session.notify_error(task.multitask.id, task.multitask.user, e, task.multitask.task.duration)
                return
        try:
            new_task = await task.multitask.task.next_task()
            if new_task:
                await self.add_subtask(task.multitask, new_task.task_no, new_task.total_tasks, new_task.task_name, 
                                       task.user, new_task.task_args, new_task.task_kwargs, priority, 
                                       task.task.user)
        except Exception as e:
            logger.exception('Get next task error')
            self._session.notify_error(task.multitask.id, task.multitask.user, e, task.multitask.task.duration)
            
            
            
   
        
