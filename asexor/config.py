MAX_PRIORITY = 0
MIN_PRIORITY = 9
NORMAL_PRIORITY = 4


class ConfigError(Exception):
    pass


class Config():
    # GENERAL Configuration
    DEFAULT_PRIORITY = NORMAL_PRIORITY
    PRIORITY_MAP = {}  # role to priority
    # number of tasks that can run in parallel, None means number of cores
    CONCURRENT_TASKS = None
    TASKS_QUEUE_MAX_SIZE = 0  # 0 means not limited
    CLIENT_CALL_TIMEOUT = 5 # max. waiting time  on client side to get task_id, when exceeded TimeoutError is thrown
    ######################
    # WAMP related configuration
    class WAMP:
        UPDATE_CHANNEL = 'eu.zderadicka.asexor.task_update'
        RUN_TASK_PROC = 'eu.zderadicka.asexor.run_task'
        # how to limit update events, now only session id works now in crossbar
        LIMIT_PUBLISH_BY = 'SESSION'
        # add authentication callback here
        # function signature is (realm, user_id, details), returns role name
        # details['ticket'] is token for token based authentication
        AUTHENTICATION_PROCEDURE = None  
        AUTHENTICATION_PROCEDURE_NAME = ''  # WAMP name
        # add authorization callback here
        # function signature is (session, uri, action) return True or False
        AUTHORIZATION_PROCEDURE = None  
        AUTHORIZATION_PROCEDURE_NAME = ''  # WAMP name
    
    ###################################
    # WS + aiohttp related configuration
    class WS:
        # authentication function - takes one param - token,
        # return tuple - user_id, user_role
        AUTHENTICATION_PROCEDURE = None
    ####################################
    
    ###################################
    # WS + aiohttp related configuration
    class RAW:
        # authentication function - takes one param - token,
        # return tuple - user_id, user_role
        AUTHENTICATION_PROCEDURE = None
    ####################################   
    
    