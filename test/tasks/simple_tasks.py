from asexor.task import BaseSimpleTask, Arg, BoolArg, ArgumentError, BaseMultiTask, TaskDetails
import logging
from array import array


logger = logging.getLogger(__name__)

class DateTask(BaseSimpleTask):
    NAME = 'date'
    COMMAND = 'date'
    ARGS = [BoolArg('utc', '-u'), Arg(0)]
    MAX_TIME = 5

    async def validate_args(self, fmt, ** kwargs):
        return await super(DateTask, self).validate_args('+' + fmt, **kwargs)

    async def parse_result(self, data):
        logger.debug('Result for date task executed for user %s', self.user)
        return data.decode(self.output_encoding).strip()


class SleepTask(BaseSimpleTask):
    NAME = 'sleep'
    COMMAND = 'sleep'
    ARGS = [Arg(0)]
    

class GenericMultiTask(BaseMultiTask):
    NAME = 'multi'
    async def start(self, *args, **kwargs):
        self.tasks = args[0]
        self.tasks_args = args[1]
        if (len(self.tasks) != len(self.tasks_args)):
            raise ArgumentError('For each tasks the must be argumets tuple ')
        self.count =0
        self.done = 0
        self.tasks_results = [None] * len(self.tasks)
        
    async def next_task(self):
        if self.count>= len(self.tasks):
            return None
        td=TaskDetails(task_name=self.tasks[self.count],
                       task_args=self.tasks_args[self.count][0],
                       task_kwargs=self.tasks_args[self.count][1],
                       task_no = self.count,
                       total_tasks = len(self.tasks)
                       )
        self.count+=1
        return td
    
    async def update_task_result(self, task_no, result=None, error=None, on_all_finished=None):
        self.tasks_results[task_no] = result
        self.done += 1
        if self.done == len(self.tasks) and on_all_finished:
            on_all_finished(self.tasks_results)
        
    
        
        
