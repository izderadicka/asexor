import unittest
from unittest.mock import Mock
import os.path
from asexor.task import Arg, ArgumentError, BoolArg, load_tasks_from, get_task, TimeoutError
import asyncio
import sys


class BaseTest(unittest.TestCase):

    def setUp(self):
        load_tasks_from(
            'simple_tasks', os.path.join(os.path.dirname(__file__), 'tasks'))

    def tearDown(self):
        import asexor.task
        asexor.task._tasks_registry = {}
        

class TestTasks(BaseTest):

    def test_args(self):
        a = Arg(0)
        aa = Arg('foo')
        self.assertEqual(a.get_value('a'), 'a')
        self.assertEqual(aa.get_value('a', foo='b'), 'b')

        b = Arg(1)
        bb = Arg('moo')
        with self.assertRaises(ArgumentError):
            b.get_value('a')

        with self.assertRaises(ArgumentError):
            bb.get_value('a', foo='b')

        self.assertEqual(Arg(0, '--name').get_value('jan'), ('--name',  'jan'))
        self.assertEqual(Arg(0, '--name=').get_value('jan'), '--name=jan')
        self.assertEqual(
            Arg('name', '--name=', default='petr').get_value('jan'), '--name=petr')
        self.assertEqual(
            Arg('name', '--name=', default='petr').get_value(name='jan'), '--name=jan')
        self.assertTrue(
            Arg('name', '--name=', optional=True).get_value('jan') is None)

        self.assertEqual(BoolArg(0, '-d').get_value(1), '-d')
        self.assertTrue(BoolArg(0, '-d').get_value(0) is None)

    def test_task_date(self):
        date = get_task('date')()
        self.assertTrue(date)
        loop = asyncio.get_event_loop()
        args = loop.run_until_complete(
            date.validate_args('%d-%m-%Y %H:%M %Z', utc=True))
        self.assertEqual(args[1], '+%d-%m-%Y %H:%M %Z')

        res = loop.run_until_complete(date.execute(*args))
        res = loop.run_until_complete(date.parse_result(res))
        self.assertTrue(res.endswith('UTC'))
        self.assertTrue(date.duration > 0)

        res = loop.run_until_complete(date.run('%d-%m-%Y %H:%M %Z', utc=True))
        self.assertTrue(res.endswith('UTC'))

    def test_task_sleep(self):
        sleep = get_task('sleep')()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sleep.execute('1'))
        self.assertTrue(sleep.duration > 1)

        sleep2 = sleep = get_task('sleep')(max_time=1)
        with self.assertRaises(TimeoutError):
            loop.run_until_complete(sleep2.execute('2'))
        self.assertTrue(sleep.duration < 1.1)
        
    def test_multi(self):
        loop = asyncio.get_event_loop()
        run = loop.run_until_complete
        m =  get_task('multi')()
        run(m.start(['date', 'sleep', 'date'], [(['%d-%m-%Y %H:%M %Z'], {'utc':True}), ([1], {}), 
                                                (['%d-%m-%Y %H:%M %Z'], {'utc':False}),]))
        
        cb = Mock()
        t = run(m.next_task())
        self.assertEqual(t.task_name, 'date')
        self.assertEqual(t.task_no, 0)
        
        run(m.update_task_result(0, result=0, on_all_finished=cb))
        cb.assert_not_called()
        
        t = run(m.next_task())
        self.assertEqual(t.task_name, 'sleep')
        self.assertEqual(t.task_no, 1)
        
        run(m.update_task_result(1, result=1, on_all_finished=cb))
        cb.assert_not_called()
        
        t = run(m.next_task())
        self.assertEqual(t.task_name, 'date')
        self.assertEqual(t.task_no, 2)
        self.assertEqual(t.task_kwargs, {'utc':False})
        
        run(m.update_task_result(2, result=2, on_all_finished=cb))
        cb.assert_called_once_with([0,1,2])
        
        t = run(m.next_task())
        self.assertTrue(t is None)
        
        
        
        
        
