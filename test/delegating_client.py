import aiohttp
import asyncio
import logging
import argparse
import sys
from collections import defaultdict, deque
import random
from asexor.raw_client import RawSocketAsexorClient

logger = logging.getLogger('dummy_client')

                
TASKS = [('date', ('%d-%m-%Y %H:%M %Z',), {'utc': True}),
         ('sleep', (0.1,), {})
         ]

USERS = [('pepa', 'user'), ('franta', 'user'), ('venda', 'superuser'), ('kaja', 'admin')]
                
class MyClient():
    def __init__(self, count, time, session, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._tasks_table = defaultdict(dict)
        self._pending_updates = deque()
        self._all_done = self.loop.create_future()
        self._all_done.add_done_callback(self._on_done)
        self.session = session
        self.count = count
        self.time = time

    

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
            user, role = ranndom.choice(USERS)
            task_id = await self.session.execute(task_name, *args, **kwargs)
            logger.debug('Task submitted with id=%s', task_id)
            self._tasks_table[task_id]['status'] = 'sent'

        # in case notification came before task result (possible due to async
        # sheduling
        # self._process_pending()
        self._check_done()
        await self._all_done
                
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug')
    parser.add_argument('-n', '--number', type=int, default=10, help="number of tasks to send")
    
    
    
    opts = parser.parse_args()
    loop = asyncio.get_event_loop()
    level = logging.INFO
    if opts.debug:
        level = logging.DEBUG
        loop.set_debug(True)
    logging.basicConfig(level=level)
    
    
    
    path = '/tmp/asexor-test.socket'
    url = 'tcp://localhost:8485'
    session = RawSocketAsexorClient(url, 'ivan', loop)
    
    try:
        loop.run_until_complete(session.start())
    except:
        logger.error('Preliminary exited')
        loop.run_until_complete(session.stop())
        sys.exit(1)
    client =  MyClient(opts.number, opts.time, session, loop)
    loop.run_until_complete(client.run())
    loop.run_until_complete(session.stop())
    
    
    
   
                