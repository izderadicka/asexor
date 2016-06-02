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


class SessionAdapter():

    def __init__(self, session):
        self._session = session

    def _options(self, task_user):
        if Config.LIMIT_PUBLISH_BY == 'SESSION' and task_user:
            return PublishOptions(eligible=[task_user])
        elif not Config.LIMIT_PUBLISH_BY:
            return None

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
        if Config.AUTHENTICATION_PROCEDUTE and Config.AUTHENTICATION_PROCEDURE_NAME:
            self.register(Config.AUTHENTICATION_PROCEDUTE, Config.AUTHENTICATION_PROCEDURE_NAME)
        if Config.AUTHORIZATION_PROCEDUTE and Config.AUTHORIZATION_PROCEDURE_NAME:
            self.register(Config.AUTHORIZATION_PROCEDUTE, Config.AUTHORIZATION_PROCEDURE_NAME)
            
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
