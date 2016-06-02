import asyncio
import logging
import argparse
import random
from autobahn.asyncio.wamp import ApplicationSession
from asexor.runner import ApplicationRunnerRawSocket
from asexor.config import Config
from collections import defaultdict, deque

log = logging.getLogger('dummy_client')

TASKS = [('date', ('%d-%m-%Y %H:%M %Z',), {'utc': True}),
         ('sleep', (0.1,), {})
         ]


class MyClient(ApplicationSession):
    COUNT = 10

    def onConnect(self):
        self.join(self.config.realm, [u"ticket"], self.USER)
        self._tasks_table = defaultdict(dict)
        self._pending_updates = deque()
        self._all_done = asyncio.Future()
        self._all_done.add_done_callback(self._on_done)

    def onChallenge(self, ch):
        if ch.method == 'ticket':
            log.debug('Got challenge %s', ch)
            return ''
        else:
            raise Exception('Invalid authentication method')

    def onDisconnect(self):
        log.warn('Disconnected')
        asyncio.get_event_loop().stop()

    def _on_done(self, r):
        log.info('All tasks (%d) are finished', len(self._tasks_table))
        has_error = any(
            map(lambda v: v['status'] == 'errdetails=or', self._tasks_table.values()))
        if has_error:
            log.error('Some tasks have error')
        asyncio.get_event_loop().stop()

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
            len(self._tasks_table) >= self.COUNT and \
            len(self._pending_updates) == 0
        # if len(self._tasks_table)>= self.COUNT: print ("XXX ", self._tasks_table)
        if done:
            self._all_done.set_result(True)

    async def onJoin(self, details):
        log.info('Joined session with details %s', details)

        def log_updates(task_id, status=None, **kwargs):
            # first update any pending updates
            # self._process_pending()
            log.info(
                'Update for task %s, status = %s, details= %s', task_id, status, kwargs)
            if task_id in self._tasks_table:
                self._update_task(task_id, status, kwargs)
            else:
                self._pending_updates.append((task_id, status, kwargs))
            self._check_done()

        self.subscribe(log_updates, Config.UPDATE_CHANNEL)

        for i in range(self.COUNT):
            task_name, args, kwargs = random.choice(TASKS)
            task_id = await self.call(Config.RUN_TASK_PROC, task_name, *args, **kwargs)
            log.info('Task submitted with id=%s', task_id)
            self._tasks_table[task_id]['status'] = 'sent'

        # in case notification came before task result (possible due to async
        # sheduling
        # self._process_pending()
        self._check_done()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('user', help="user id to join with")
    parser.add_argument(
        '-d', '--debug', action='store_true', help='enable debug')
    parser.add_argument('-n', '--number', type=int, default=10, help="number of remote calls")
    opts = parser.parse_args()

    MyClient.USER = opts.user
    MyClient.COUNT = opts.number
    level = 'info'
    if opts.debug:
        level = 'debug'
    runner = ApplicationRunnerRawSocket(
        "tcp://localhost:9090",
        u"realm1")
    runner.run(MyClient, logging_level=level)
