import asyncio
from unittest.mock import Mock
from test_tasks import BaseTest
from asexor.tqueue import TasksQueue
from asexor.config import MAX_PRIORITY
import time
import math


class TestQueue(BaseTest):

    def test_queue(self):
        session = Mock()
        session.notify_success = Mock(
            side_effect=lambda *args, **kwargs: print('Success: %s %s' % (args, kwargs)))
        q = TasksQueue(session)
        for _i in range(10):
            q.add_task('date', 'ivan', ('%d-%m-%Y %H:%M %Z',), {'utc': True})

        asyncio.ensure_future(q.run_tasks())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(q.join(0.1))

        self.assertEqual(session.notify_start.call_count, 10)
        self.assertEqual(session.notify_success.call_count, 10)
        self.assertFalse(session.notify_error.called)

    def test_queue_concurrency(self):
        session = Mock()
        session.notify_success = Mock(
            side_effect=lambda *args, **kwargs: print('Success: %s %s' % (args, kwargs)))
        q = TasksQueue(session, concurrent=4)
        for _i in range(12):
            q.add_task('sleep', 'ivan', (1,))

        asyncio.ensure_future(q.run_tasks())
        loop = asyncio.get_event_loop()
        start = time.time()
        loop.run_until_complete(q.join(0.1))
        duration = time.time() - start

        self.assertTrue(
            abs(duration - 3.1) < 0.1, 'Should take app 3.1 secs, but took %f' % duration)

        self.assertEqual(session.notify_start.call_count, 12)
        self.assertEqual(session.notify_success.call_count, 12)

    def test_queue_priority(self):
        session = Mock()
        done = []
        session.notify_success = Mock(
            side_effect=lambda id, user, res, dur: done.append(user))
        q = TasksQueue(session, concurrent=4)
        for _i in range(6):
            q.add_task('sleep', 'ivan', (1,))
        q.add_task('sleep', 'speedy', (0.8,), task_priority=MAX_PRIORITY)
        asyncio.ensure_future(q.run_tasks())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(q.join(0.1))

        self.assertEqual(session.notify_start.call_count, 7)
        self.assertEqual(session.notify_success.call_count, 7)
        self.assertFalse(session.notify_error.called)
        
        self.assertEqual(len(done), 7)
        self.assertEqual(done[0], 'speedy')
        
        
    def test_error(self):
        session = Mock()
        session.notify_error = Mock(
            side_effect=lambda *args, **kwargs: print('Error: %s %s' % (args, kwargs)))
        q = TasksQueue(session)
        q.add_task('sleep', 'ivan', ('a',))
        asyncio.ensure_future(q.run_tasks())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(q.join(0.1))
        self.assertFalse(session.notify_success.called)
        self.assertTrue(session.notify_error.called)
        
    
    def test_multi(self):
        session = Mock()
        session.notify_error = Mock(
            side_effect=lambda *args, **kwargs: print('Error: %s %s' % (args, kwargs)))
        loop = asyncio.get_event_loop()
        run = loop.run_until_complete
        q = TasksQueue(session)
        task_id=q.add_task('multi', 'ivan', (['date', 'sleep', 'date'], [(['%d-%m-%Y %H:%M %Z'], {'utc':True}), ([1], {}), 
                                                (['%d-%m-%Y %H:%M %Z'], {'utc':False}),]))
        asyncio.ensure_future(q.run_tasks())
        loop.run_until_complete(q.join(1.1))
        session.notify_error.assert_not_called()
        
        self.assertEqual(session.notify_success.call_count, 1)
        args = session.notify_success.call_args[0]
        self.assertEqual(args[0], task_id)
        self.assertEqual(args[1], 'ivan')
        results = args[2]['results']
        self.assertEqual(len(results), 3)
        self.assertEqual(len(results[0]), 20)
        self.assertEqual(results[0][-3:], 'UTC')
        self.assertEqual(len(results[2]), 20)
        self.assertTrue(results[1] is None)
        duration = args[2]['duration']
        self.assertTrue(duration > 1)
        
        
        
        
        
        
