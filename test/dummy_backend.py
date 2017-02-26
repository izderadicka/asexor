import os.path
from asexor.config import Config
from asexor.task import load_tasks_from
from asexor.backend_runner import Runner
from asexor.ws_backend import WsAsexorBackend
import time
import logging
import asyncio
from aiohttp import web

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


def serve_dir(path, port, loop=None):
    loop = loop or asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_static('/', path, show_index=True, follow_symlinks=True)
    handler = app.make_handler()
    loop.run_until_complete(app.startup())
    srv = loop.run_until_complete(loop.create_server(handler, '0.0.0.0',
                                                     port))
    return srv


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
    loop = asyncio.get_event_loop()
    if opts.debug:
        level=logging.DEBUG
        loop.set_debug(True)
    else:
        level = logging.INFO
        
    logging.basicConfig(level=level)
    curr_dir = os.path.dirname(__file__)
    client_dir = os.path.join(curr_dir, 'dummy_client')
    
    # basic code to start aiohttp WS ASEXOR backend
    Config.WS_AUTHENTICATION_PROCEDUTE = dummy_authenticate_simple
    protocols =[(WsAsexorBackend, {'port':8484, 'static_dir':client_dir})]
    
        
    if opts.use_wamp:
        # basic code to start WAMP ASEXOR backend
        from asexor.wamp_backend import WampAsexorBackend
        Config.AUTHENTICATION_PROCEDUTE = dummy_authenticate
        Config.AUTHENTICATION_PROCEDURE_NAME = "eu.zderadicka.dummy_authenticate"
    
        Config.AUTHORIZATION_PROCEDURE = dummy_authorize
        Config.AUTHORIZATION_PROCEDURE_NAME = "eu.zderadicka.dummy_authorize"
        
        
    
        path = os.path.join(os.path.dirname(__file__), '.crossbar/socket1')
        protocols.append((WampAsexorBackend, {'url':path, 'realm': u"realm1",}))

        
    runner = Runner(protocols)
    runner.run()
    