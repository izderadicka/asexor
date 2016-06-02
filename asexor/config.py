MAX_PRIORITY = 0
MIN_PRIORITY = 9
NORMAL_PRIORITY = 4


class ConfigError(Exception):
    pass


class Config():
    UPDATE_CHANNEL = 'eu.zderadicka.asexor.task_update'
    RUN_TASK_PROC = 'eu.zderadicka.asexor.run_task'
    DEFAULT_PRIORITY = NORMAL_PRIORITY
    PRIORITY_MAP = {}  # role to priority
    # number of tasks that can run in parallel, None means number of cores
    CONCURRENT_TASKS = None
    TASKS_QUEUE_MAX_SIZE = 0  # 0 means not limited
    # how to limit update events, now only session id works now in crossbar
    LIMIT_PUBLISH_BY = 'SESSION'
    AUTHENTICATION_PROCEDUTE = None  # add authentication callback here
    AUTHENTICATION_PROCEDURE_NAME = ''  # WAMP name
    AUTHORIZATION_PROCEDURE = None  # add authorization callback here
    AUTHORIZATION_PROCEDURE_NAME = ''  # WAMP name
