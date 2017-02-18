import os.path
from asexor.config import Config
from asexor.task import load_tasks_from
from asexor.ws_backend import BackendSession
from aiohttp import web
import aiohttp_jinja2
import jinja2
import logging

log = logging.getLogger('ws_server')


def dummy_authenticate(token):
    log.debug('Authenticating user with token %s', token)
    return token, 'user'



if __name__ == '__main__':
    import argparse

    # for testing
    load_tasks_from(
        'simple_tasks', os.path.join(os.path.dirname(__file__), 'tasks'))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug')
    opts = parser.parse_args()
    
    if opts.debug:
        level=logging.DEBUG
    else:
        level = logging.INFO
        
    logging.basicConfig(level=level)
    Config.WS_AUTHENTICATION_PROCEDUTE = dummy_authenticate
    
    app = web.Application()
    session = BackendSession(app.loop)
    app.on_startup.append(session.start_tasks_queue)
    app.on_shutdown.append(session.close_all_websockets)
    app.on_cleanup.append(session.stop_tasks_queue)
    curr_dir = os.path.dirname(__file__)
#     aiohttp_jinja2.setup(app,
#         loader=jinja2.FileSystemLoader(os.path.join(curr_dir, 'templates')))
    
    app.router.add_get('/ws', session.ws_handler)
    app.router.add_static('/', os.path.join(curr_dir, 'ws_client'), show_index=True)
    web.run_app(app, port=8484)
    