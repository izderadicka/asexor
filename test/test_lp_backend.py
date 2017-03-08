from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from asexor.lp_backend import LpAsexorBackend, ASEXOR_SESSION
from asexor.message import CallMessage, ReplyMessage, ErrorMessage,\
    UpdateMessage
from dummy_backend import dummy_authenticate_simple
from asexor.config import Config
from unittest.mock import Mock
import json
import time
import aiohttp

Config.LP.AUTHENTICATION_PROCEDURE =  dummy_authenticate_simple

class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self, loop):
        self.session = LpAsexorBackend(loop)
        self.tq = Mock()
        self.tq.add_task = Mock(return_value='abcd')
        self.session.create_app(self.tq)
        return self.session.app
    
    
    
    @unittest_run_loop
    async def test_call(self):
        resp = await self.client.request("GET", "/pakaren")
        self.assertEqual(resp.status, 404)
        resp = await self.client.post("/", headers={'content-type':'application/json'},
                                      data = CallMessage(1, 'test').as_json()) 
        self.assertEqual(resp.status, 401)
        
        resp = await self.client.post("/", headers={'content-type':'application/json',
                                                    'Authorization': 'Bearer ivan'},
                                      data = CallMessage(1, 'test').as_json()) 
        self.assertEqual(resp.status, 200)
        data = await resp.text()
        print( data)
        response = ReplyMessage.from_json(data)
        self.assertEqual(response.call_id, 1)
        self.assertEqual(response.task_id, 'abcd')
        
        self.assertEqual(self.tq.add_task.call_count, 1)
        args = self.tq.add_task.call_args
        self.assertEqual(args[0][0], 'test')
        self.assertEqual(args[1]['authenticated_user'], 'ivan')
        
        session_id = resp.cookies.get(Config.LP.COOKIE_NAME).value
        self.assertTrue(session_id)
        print (session_id)
        self.assertEqual(len(session_id), 40)
        session = self.app[ASEXOR_SESSION][session_id]
        self.assertTrue(session)
        
        
        resp = await self.client.post("/", headers={'content-type':'application/json'},
                                      data = '[123]') 
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.cookies.get(Config.LP.COOKIE_NAME).value, session_id)
        
        response = ErrorMessage.from_json(await resp.text())
        self.assertEqual(response.call_id, 123)
        self.assertEqual(response.error, 'not enough values to unpack (expected 3, got 1)')
        
        session.add_message(UpdateMessage(1, {'status':'started'}).as_data())
        session.add_message(UpdateMessage(1, {'status':'success', 'result':'Hey'}).as_data())
        
        resp = await self.client.get('/')
        self.assertEqual(resp.status, 200)
        
        messages = await resp.text()
        print(messages)
        messages = [UpdateMessage.from_data(data) for data in json.loads(messages)]
        
        self.assertEqual(len(messages), 2)
        
        for m,status in zip(messages, ('started', 'success')):
            self.assertEqual(m.call_id, 1)
            self.assertEqual(m.data['status'], status)
        
        start = time.time()
        self.loop.call_later(1,lambda: session.add_message(UpdateMessage(2, {'status':'started'}).as_data()))
        resp = await self.client.get('/')
        dur = time.time()-start
            
        self.assertAlmostEqual(dur, 1, 1,  'Timeout')
        
        
        
        
        
        
        