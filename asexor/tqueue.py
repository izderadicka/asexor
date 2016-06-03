import asyncio
import uuid
from collections import namedtuple
from asexor.task import get_task
from multiprocessing import cpu_count
from asexor.config import NORMAL_PRIORITY
import logging

logger = logging.getLogger('tqueue')

TaskInfo = namedtuple(
    'TaskInfo', ['id', 'task', 'args', 'kwargs', 'user'])


class TasksQueue():

    def __init__(self, session, concurrent=None, queue_size=0):
        self._q = asyncio.PriorityQueue(maxsize=queue_size)
        self._session = session
        self._running = True
        if not concurrent:
            concurrent = cpu_count()
        self._cc_semaphore = asyncio.Semaphore(concurrent)

    def add_task(self, task_name, task_user, task_args=(), task_kwargs={}, task_priority=NORMAL_PRIORITY):
        task = get_task(task_name)()
        task_id = uuid.uuid4().hex
        loop = asyncio.get_event_loop()
        async def _add():
            # we need to assure that task_id from run_task is sent before first update
            # this is a hack - need to find a better way 
            await asyncio.sleep(0.1)
            # for security reason consider sync version of put and throw error when q is full
            await self._q.put((task_priority, TaskInfo(task_id, task, task_args, task_kwargs, task_user)))
        loop.create_task(_add())
        return task_id

    def stop(self):
        self._running = False

    async def join(self, initial_wait=None):
        if initial_wait:
            await asyncio.sleep(initial_wait)
        await self._q.join()

    async def run_tasks(self):
        while self._running:
            await self._cc_semaphore.acquire()
            _priority, task = await self._q.get()
            # notify task start
            self._session.notify_start(task.id, task.user)
            asyncio.ensure_future(self.run_one(task))

    async def run_one(self, task):
        try:
            res = await task.task.run(*task.args, **task.kwargs)
            self._session.notify_success(task.id, task.user, res, task.task.duration)
        except Exception as e:
            logger.exception('Task %s(%s, %s) id %s failed with %s',
                         task.task.NAME, task.args, task.kwargs, task.id, e)
            self._session.notify_error(task.id, task.user, e, task.task.duration)
        finally:
            self._q.task_done()
            self._cc_semaphore.release()
