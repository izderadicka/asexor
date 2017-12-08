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
    
    async def parse_result(self,data):
        logger.debug('Finished sleep task executed for user %s', self.user)
    

class GenericMultiTask(BaseMultiTask):
    NAME = 'multi'
    
        
    
        
        
