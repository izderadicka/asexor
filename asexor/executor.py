import sys
import asyncio
from datetime import datetime
import os.path
import logging
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.types import PublishOptions, RegisterOptions
from asexor.runner import ApplicationRunnerRawSocket
from asexor.tqueue import TasksQueue, NORMAL_PRIORITY
from asexor.config import Config, ConfigError
from asexor.task import load_tasks_from

log = logging.getLogger('backend')


def dummy_authenticate(realm, user_id, details):
    log.debug('Authenticating user %s', user_id)
    return 'user'


class SessionAdapter():

    def __init__(self, session):
        self._session = session

    def _options(self, task_user):
        if Config.LIMIT_PUBLISH_BY == 'SESSION':
            return PublishOptions(eligible=[task_user])

        raise ConfigError('Invalid configuration for LIMIT_PUBLISH_BY')

        # return PublishOptions(eligible_authid=[task_user]

    def notify_start(self, task_id, task_user):
        self._session.publish(Config.UPDATE_CHANNEL, task_id, status='started', user=task_user,
                              options=self._options(task_user))

    def notify_success(self, task_id, task_user, res, duration):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='success', result=res, duration=duration, user=task_user,
                              options=self._options(task_user))

    def notify_error(self, task_id, task_user, err, duration):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='error', error=str(err) or repr(err), duration=duration, user=task_user,
                              options=self._options(task_user))


class Executor(ApplicationSession):

    async def onJoin(self, details):
        log.info('started session with details %s', details)
        self.register(dummy_authenticate, 'eu.zderadicka.dummy_auth')
        self.tasks = TasksQueue(SessionAdapter(self),
                                concurrent=Config.CONCURRENT_TASKS,
                                queue_size=Config.TASKS_QUEUE_MAX_SIZE)

        def run_task(task_name, *args, **kwargs):
            log.debug(
                'Request for run task %s %s %s', task_name, args, kwargs)
            details = kwargs.pop('__call_details__', None)
            if not details:
                raise RuntimeError('Call details not available')
            task_user = details.caller if Config.LIMIT_PUBLISH_BY == "SESSION" else None
            role = details.caller_authrole
            task_priority = Config.DEFAULT_PRIORITY
            if role:
                task_priority = Config.PRIORITY_MAP.get(
                    role, Config.DEFAULT_PRIORITY)
            task_id = self.tasks.add_task(
                task_name, task_user, args, kwargs, task_priority)
            return task_id
        self.register(run_task, Config.RUN_TASK_PROC, RegisterOptions(
            details_arg='__call_details__'))

        try:
            await self.tasks.run_tasks()
        except Exception as e:
            # ignore exception caused by closing loop
            if not asyncio.get_event_loop().is_closed():
                log.exception(e)

    def onDisconnect(self):
        log.warn('Disconnected')
        asyncio.get_event_loop().stop()

if __name__ == '__main__':
    import argparse

    # for testing
    load_tasks_from(
        'simple_tasks', os.path.join(os.path.dirname(__file__), '../test/tasks'))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug')
    opts = parser.parse_args()
    level = 'info'
    if opts.debug:
        level = 'debug'
    path = os.path.join(os.path.dirname(__file__), '.crossbar/socket1')
    runner = ApplicationRunnerRawSocket(
        path,
        u"realm1",
    )
    runner.run(Executor, logging_level=level)
