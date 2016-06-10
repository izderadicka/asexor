import os.path
from asexor.config import Config
from asexor.task import load_tasks_from
from asexor.executor import Executor
from asexor.runner import ApplicationRunnerRawSocket
import logging
import time

log = logging.getLogger('dummy_server')


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

    # for testing
    load_tasks_from(
        'simple_tasks', os.path.join(os.path.dirname(__file__), 'tasks'))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug')
    opts = parser.parse_args()
    level = 'info'
    if opts.debug:
        level = 'debug'

    Config.AUTHENTICATION_PROCEDUTE = dummy_authenticate
    Config.AUTHENTICATION_PROCEDURE_NAME = "eu.zderadicka.dummy_authenticate"

    Config.AUTHORIZATION_PROCEDURE = dummy_authorize
    Config.AUTHORIZATION_PROCEDURE_NAME = "eu.zderadicka.dummy_authorize"

    path = os.path.join(os.path.dirname(__file__), '.crossbar/socket1')
    runner = ApplicationRunnerRawSocket(
        path,
        u"realm1",
    )
    runner.run(Executor, logging_level=level)
