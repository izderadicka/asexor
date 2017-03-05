import aiohttp
import asyncio
import logging
import argparse
import sys
from collections import defaultdict, deque
import random
from asexor.ws_client import AsexorClient
from asexor.wamp_client import WampAsexorClient
from asexor.raw_client import RawSocketAsexorClient
from asyncio.tasks import FIRST_COMPLETED

logger = logging.getLogger('dummy_client')

                
TASKS = [('date', ('%d-%m-%Y %H:%M %Z',), {'utc': True}),
         ('sleep', (0.1,), {})
         ]
                
class MyClient():
    def __init__(self, count, session, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._tasks_table = defaultdict(dict)
        self._pending_updates = deque()
        self._all_done = self.loop.create_future()
        self._all_done.add_done_callback(self._on_done)
        self.session = session
        self.count = count

    

    def _on_done(self, r):
        logger.info('All tasks (%d) are finished', len(self._tasks_table))
        has_error = any(
            map(lambda v: v['status'] == 'error', self._tasks_table.values()))
        if has_error:
            logger.error('Some tasks have error')
        

    def _update_task(self, task_id, status, kwargs):
        self._tasks_table[task_id]['status'] = status
        if 'result' in kwargs:
            self._tasks_table[task_id]['result'] = kwargs['result']
        if 'error' in kwargs:
            self._tasks_table[task_id]['error'] = kwargs['error']

    def _process_pending(self):
        while self._pending_updates:
            task_id, status, kwargs = self._pending_updates[0]
            if task_id in self._tasks_table:
                self._pending_updates.popleft()
                self._update_task(task_id, status, kwargs)
            else:
                break

    def _check_done(self):
        def is_done(x):
            d = ('status' in x) and x['status'] in ('success', 'error')
            return d
        done = all(map(is_done, self._tasks_table.values())) and \
            len(self._tasks_table) >= self.count and \
            len(self._pending_updates) == 0
        # if len(self._tasks_table)>= self.COUNT: print ("XXX ", self._tasks_table)
        if done:
            self._all_done.set_result(True)

    async def run(self):
       
        async def log_updates(task_id, status=None, **kwargs):
            # first update any pending updates
            # self._process_pending()
            logger.debug(
                'Update for task %s, status = %s, details= %s', task_id, status, kwargs)
            if task_id in self._tasks_table:
                self._update_task(task_id, status, kwargs)
            else:
                self._pending_updates.append((task_id, status, kwargs))
            self._check_done()

        self.session.subscribe(log_updates)

        for i in range(self.count):
            task_name, args, kwargs = random.choice(TASKS)
            task_id = await self.session.execute(task_name, *args, **kwargs)
            logger.debug('Task submitted with id=%s', task_id)
            self._tasks_table[task_id]['status'] = 'sent'

        # in case notification came before task result (possible due to async
        # sheduling
        # self._process_pending()
        self._check_done()
        
        await  asyncio.wait([self._all_done, self.session.wait_closed()], return_when=FIRST_COMPLETED)
        logger.info('Client is done')
                
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('user', help="user id to join with")
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug')
    parser.add_argument('-n', '--number', type=int, default=10, help="number of remote calls")
    parser.add_argument('--use-wamp', action='store_true', help='Use WAMP protocol - requires WAMP router(crossbar.io) to be running')
    parser.add_argument('--use-raw', action='store_true', help="Use raw socket protocol")
    opts = parser.parse_args()
    loop = asyncio.get_event_loop()
    level = logging.INFO
    if opts.debug:
        level = logging.DEBUG
        loop.set_debug(True)
    logging.basicConfig(level=level)
    
    
    if opts.use_wamp:
        session = WampAsexorClient("tcp://localhost:9090",  u"realm1", opts.user, opts.user, loop=loop)
    elif opts.use_raw:
        path = '/tmp/asexor-test.socket'
        url = 'tcp://localhost:8485'
        session = RawSocketAsexorClient(url, opts.user, loop)
    else:
        session = AsexorClient('http://localhost:8484/ws', opts.user, loop)
    try:
        loop.run_until_complete(session.start())
    except:
        logger.exception('Preliminary exited')
        loop.run_until_complete(session.stop())
        sys.exit(1)
    client =  MyClient(opts.number or 10, session, loop)
    try:
        loop.run_until_complete(client.run())
        loop.run_until_complete(session.stop())
    except KeyboardInterrupt:
        logger.info('Program interrupted by keyboard interrupt (SIGINT)')
    
    
    
   
                