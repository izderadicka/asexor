MAX_PRIORITY = 0
MIN_PRIORITY = 9
NORMAL_PRIORITY = 4


class ConfigError(Exception):
    pass


class Config():
    # GENERAL Configuration
    DEFAULT_PRIORITY = NORMAL_PRIORITY
    # role to priority, can be also coroutine function 
    PRIORITY_MAP = {}  
    # number of tasks that can run in parallel, None means number of cores
    CONCURRENT_TASKS = None
    # 0 means not limited
    TASKS_QUEUE_MAX_SIZE = 0  
    # max. waiting time  on client side to get task_id, when exceeded TimeoutError is thrown
    CLIENT_CALL_TIMEOUT = 5 
    # coroutine function , takes task_name and role, return boolean , None means no special authorization
    AUTHORIZATION_PROCEDURE = None
    # Send stack for errors caused by task scheduling -  should not be used in production
    SEND_REMOTE_ERROR_STACK =  True
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
        # If > 0 this is interval in which server will send ping to keep connection open 
        # and check that client is still alive
        # (nginx for instance closes connection after 60 secs)
        HEARTBEAT = None
        # Server will close WS after x secs of inactivity (no incoming or outcoming message)
        # None or zero  means no timeout
        INACTIVE_TIMEOUT = 3600
        # If session is interrupted unsent messages are temporally saved, hoping for session to reconnect
        # It time is secs (from first unsent message), how long messages will be saved before forgotten, 
        # if reconnect does not happen 
        UNSENT_MSG_TIMEOUT = 60
    ####################################
    
    ###################################
    # WS + aiohttp related configuration
    class RAW:
        # authentication function - takes one param - token,
        # return tuple - user_id, user_role
        AUTHENTICATION_PROCEDURE = None
    ####################################   
    
    ####################################
    class LP:
        COOKIE_NAME = 'ASEXOR_LP_SESSION'
        MAX_SESSION_TIME = 24 * 3600 # maximum total length of session is seconds
        MAX_SESSION_INACTIVITY = 3600 # maximum inactivity in session before it's recycled
        LONG_POLL_TIMEOUT = 600 # timeout for long poll waiting 
        # authentication function - takes one param - token,
        # return tuple - user_id, user_role
        AUTHENTICATION_PROCEDURE = None
        # CORS - this allow cross side requests for any side with all headers - modify if need more strict access
        ENABLE_CORS = True
        CORS_ORIGIN = '*'
        CORS_ALLOW_CREDENTIAL = True
        CORS_ALLOW_HEADERS = '*'
        CORS_EXPOSE_HEADERS = '*'
        
        
    
    