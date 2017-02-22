import os.path
from asexor.config import Config
from asexor.task import load_tasks_from
import time

import logging

log = logging.getLogger('ws_server')

# dummy authentication -  token is basically username
def dummy_authenticate_simple(token):
    log.debug('Authenticating user with token %s', token)
    return token, 'user'

# WAMP requires different  authentication function and authorize function
def dummy_authenticate(realm, user_id, details):
    log.debug('Authenticating user %s details %s', user_id, details)
    return {'role': 'user', 'extra': {'ts': time.time()}}


def dummy_authorize(session, uri, action):
    log.debug("Authorizing uri {} for  {}, session={})".format(
        uri, action, session))

    if (uri == Config.UPDATE_CHANNEL and action == 'subscribe') or \
       (uri == Config.RUN_TASK_PROC and action == 'call'):
        return {"allow": True, "disclose": True, "cache": True}

    return False


if __name__ == '__main__':
    import argparse

    # tasks for testing
    load_tasks_from(
        'simple_tasks', os.path.join(os.path.dirname(__file__), 'tasks'))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug',)
    parser.add_argument('--use-wamp', action='store_true', help='Use WAMP protocol - requires WAMP router(crossbar.io) to be running')
    opts = parser.parse_args()
    
    if opts.debug:
        level='debug'
    else:
        level = 'info'
        
    if opts.use_wamp:
        # basic code to start WAMP ASEXOR backend
        from asexor.wamp_backend import WampAsexorBackend, WampBackendRunner
        Config.AUTHENTICATION_PROCEDUTE = dummy_authenticate
        Config.AUTHENTICATION_PROCEDURE_NAME = "eu.zderadicka.dummy_authenticate"
    
        Config.AUTHORIZATION_PROCEDURE = dummy_authorize
        Config.AUTHORIZATION_PROCEDURE_NAME = "eu.zderadicka.dummy_authorize"
    
        path = os.path.join(os.path.dirname(__file__), '.crossbar/socket1')
        runner = WampBackendRunner(
            path,
            u"realm1",
        )
        runner.run(WampAsexorBackend, logging_level=level)
    else:
        # basic code to start aiohttp WS ASEXOR backend
        from asexor.ws_backend import AsexorBackend, BackendRunner
        Config.WS_AUTHENTICATION_PROCEDUTE = dummy_authenticate_simple
        curr_dir = os.path.dirname(__file__)
        runner = BackendRunner(port=8484, static_dir=os.path.join(curr_dir, 'ws_client'))
        runner.run(AsexorBackend, log_level=level)
    
    