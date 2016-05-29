from asexor.task import BaseTask, Arg, BoolArg, ArgumentError


class DateTask(BaseTask):
    NAME = 'date'
    COMMAND = 'date'
    ARGS = [BoolArg('utc', '-u'), Arg(0)]
    MAX_TIME = 5

    async def validate_args(self, *args, ** kwargs):
        return ('+' + args[0],), kwargs

    async def parse_result(self, data):
        return data.decode(self.output_encoding).strip()


class SleepTask(BaseTask):
    NAME = 'sleep'
    COMMAND = 'sleep'
    ARGS = [Arg(0)]


    
