import asyncio
import logging
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.types import PublishOptions, RegisterOptions
from asexor.tqueue import TasksQueue, NORMAL_PRIORITY, AbstractSessionAdapter
from asexor.config import Config, ConfigError


log = logging.getLogger('wamp_backend')


class SessionAdapter(AbstractSessionAdapter):

    def __init__(self, session):
        self._session = session

    def _options(self, task_context):
        if Config.LIMIT_PUBLISH_BY == 'SESSION' and task_context and task_context.caller:
            return PublishOptions(eligible=[task_context.caller])
        elif not Config.LIMIT_PUBLISH_BY:
            return None

        raise ConfigError('Invalid configuration for LIMIT_PUBLISH_BY')

        # return PublishOptions(eligible_authid=[task_user]

    def notify_start(self, task_id, task_context=None):
        self._session.publish(Config.UPDATE_CHANNEL, task_id, status='started',
                              options=self._options(task_context))

    def notify_success(self, task_id, res, duration, task_context=None):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='success', result=res, duration=duration,
                              options=self._options(task_context))
        
    def notify_progress(self, task_id, progress, task_context=None):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='progress', progress=progress,
                              options=self._options(task_context))

    def notify_error(self, task_id, err, duration, task_context=None):
        self._session.publish(Config.UPDATE_CHANNEL, task_id,
                              status='error', error=str(err) or repr(err), duration=duration,
                              options=self._options(task_context))


class BackendSession(ApplicationSession):

    async def onJoin(self, details):
        log.info('started session with details %s', details)
        if Config.AUTHENTICATION_PROCEDUTE and Config.AUTHENTICATION_PROCEDURE_NAME:
            self.register(Config.AUTHENTICATION_PROCEDUTE, Config.AUTHENTICATION_PROCEDURE_NAME)
        if Config.AUTHORIZATION_PROCEDURE and Config.AUTHORIZATION_PROCEDURE_NAME:
            self.register(Config.AUTHORIZATION_PROCEDURE, Config.AUTHORIZATION_PROCEDURE_NAME)
            
        self.tasks = TasksQueue(SessionAdapter(self),
                                concurrent=Config.CONCURRENT_TASKS,
                                queue_size=Config.TASKS_QUEUE_MAX_SIZE)

        def run_task(task_name, *args, **kwargs):
            log.debug(
                'Request for run task %s %s %s', task_name, args, kwargs)
            details = kwargs.pop('__call_details__', None)
            if not details:
                raise RuntimeError('Call details not available')
            role = details.caller_authrole
            authid = details.caller_authid
            task_priority = Config.DEFAULT_PRIORITY
            if role:
                task_priority = Config.PRIORITY_MAP.get(
                    role, Config.DEFAULT_PRIORITY)
            task_id = self.tasks.add_task(
                task_name, args, kwargs, task_priority, authenticated_user=authid, 
                task_context=details)
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
