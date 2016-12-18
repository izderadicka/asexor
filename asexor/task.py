import asyncio
import logging
import re
import sys
import time
from inspect import isclass
from functools import reduce
from importlib import import_module
from collections import namedtuple


logger = logging.getLogger('task')

_tasks_registry = {}


def register(cls):
    if issubclass(cls, BaseTask) and hasattr(cls, 'NAME') and cls.NAME:
        if cls.NAME in _tasks_registry:
            raise ValueError('Task %s already registered' % cls.NAME)
        _tasks_registry[cls.NAME] = cls
    else:
        raise ValueError('Invalid task class')


def load_tasks_from(module, extra_path=None):
    if extra_path and extra_path not in sys.path:
        sys.path.append(extra_path)
    m = import_module(module)
    names = dir(m)
    for name in names:
        cls = getattr(m, name)
        if re.match('[A-Z]', name) and isclass(cls) and cls not in (BaseTask, BaseSimpleTask, BaseMultiTask) and issubclass(cls, BaseTask):
            register(cls)


def get_task(name):
    try:
        return _tasks_registry[name]
    except KeyError:
        raise NoSuchTask('No task with name %s' % name)


class ArgumentError(Exception):
    pass


class Arg():

    def __init__(self, source, tag=None, default=None, optional=False):
        assert isinstance(source, (str, int))
        self.source = source
        self.default = default
        self.tag = tag
        self.optional = optional

    def _extract_value(self, *args, **kwargs):
        try:
            if isinstance(self.source, int):
                val = args[self.source]
            else:
                val = kwargs[self.source]
        except (KeyError, IndexError):
            if self.optional:
                return
            elif self.default is not None:
                val = self.default
            else:
                raise ArgumentError('Missing source %s' % self.source)
        return val

    def get_value(self, *args, **kwargs):
        val = self._extract_value(*args, **kwargs)
        if not val:
            return
        val = str(val)
        if self.tag:
            return self.tag + val if self.tag.endswith('=') else (self.tag, val)
        else:
            return val


class BoolArg(Arg):

    def __init__(self, source, tag):
        super(BoolArg, self).__init__(source, tag, default=False)

    def get_value(self, *args, **kwargs):
        val = self._extract_value(*args, **kwargs)
        if val:
            return self.tag


class TaskError(Exception):
    pass


class TimeoutError(TaskError):
    pass


class NoSuchTask(TaskError):
    pass

class BaseTask():
    NAME = ''
    
    def __init__(self, user):
        self.user = user
        self.duration = None
        
TaskDetails = namedtuple('TaskDetails', ('task_name', 'task_args', 'task_kwargs', 
                                         'task_no', 'total_tasks'))

class BaseMultiTask(BaseTask):
    
    def __init__(self, user=None):
        super(BaseMultiTask, self).__init__(user)
    
    async def start(self, *args, **kwargs):
        self.register_tasks(args[0], args[1])
        self._start_time = time.time()
        
        
    def register_tasks(self, tasks, tasks_args):
        if hasattr(self, 'tasks'):
            raise Exception('Can be used only once in instance')
        self.tasks = tasks
        self.tasks_args = tasks_args
        if (len(self.tasks) != len(self.tasks_args)):
            raise ArgumentError('For each tasks there must be arguments tuple ')
        self.count =0
        self.done = 0
        self.tasks_results = [None] * len(self.tasks)
        self.total_tasks = len(self.tasks)
        
       
    async def next_task(self):
        if self.count>= self.total_tasks:
            return None
        td=TaskDetails(task_name=self.tasks[self.count],
                       task_args=self.tasks_args[self.count][0],
                       task_kwargs=self.tasks_args[self.count][1],
                       task_no = self.count,
                       total_tasks = self.total_tasks
                       )
        self.count+=1
        return td
    
    async def update_task_result(self, task_no, result=None, error=None, on_all_finished=None, 
                                 on_progress=None):
        
        if task_no is not None:
            self.tasks_results[task_no] = result
            self.done += 1
            if on_progress:
                on_progress(self.done / self.total_tasks)
        if self.done == self.total_tasks and on_all_finished:
            self.duration =  time.time() - self._start_time
            on_all_finished({'results':self.tasks_results, 'duration': self.duration})
    
    
    

class BaseSimpleTask(BaseTask):
    COMMAND = ''
    ARGS = []
    MAX_TIME = None

    def __init__(self, user=None, output_encoding='UTF-8', max_time=None):
        super(BaseSimpleTask, self).__init__(user)
        self.output_encoding = output_encoding
        self.max_time = max_time
        

    async def validate_args(self, *args, **kwargs):
        def substitute_args():
            def arg_val(x):
                if isinstance(x, Arg):
                    return x.get_value(*args, **kwargs)
                else:
                    return x
            l = map(arg_val, self.ARGS)

            def flatten(l, item):
                if isinstance(item, (list, tuple)):
                    l.extend(item)
                elif item:
                    l.append(item)
                return l
            return reduce(flatten, l, [])
        return substitute_args()

    async def execute(self, *args):
        logger.debug('Running task %s command %s with params %s', self.NAME, self.COMMAND, args)
        start = time.time()
        proc = await asyncio.create_subprocess_exec(self.COMMAND, *args,
                                                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        wait_times = list(filter(None, [self.max_time, self.MAX_TIME]))
        wait_time = min(wait_times) if wait_times else None
        try:
            output, error = await asyncio.wait_for(proc.communicate(), wait_time)

        except asyncio.TimeoutError:
            logger.error('Task %s with args %s pid %d timeout after %f', self.NAME,
                         args, proc.pid, wait_time)
            try:
                proc.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(proc.wait(), 1)
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                else:
                    logger.warn('Has to kill process %d', proc.pid)
            raise TimeoutError('Timeout after %f' % wait_time)
        finally:
            self.duration = time.time() - start
        ret_code = proc.returncode
        # process should finish now
        assert ret_code is not None
        if ret_code != 0:
            raise TaskError('Command "%s %s" failed with return code %d\nOutput: %s\nError Output: %s' % (self.COMMAND,
                                                                            args, ret_code, output, error))
        return output

    async def parse_result(self, data):
        return None

    async def run(self, *args, **kwargs):
        args = await self.validate_args(*args, **kwargs)
        res = await self.execute(*args)
        return await self.parse_result(res)
