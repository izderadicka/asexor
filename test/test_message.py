
import unittest
from asexor.message import *

messages = [CallMessage(1, 'test'),
                    CallMessage(2, 'xxxx', ['a', 'b'], {'c':2}),
                    ReplyMessage(1, 'jkhfakjshfdkjds'),
                    ErrorMessage(2, 'error'),
                    ErrorMessage(call_id=2, error='aaaaaa', error_stack='start jkfdhsa\n'*10),
                    UpdateMessage(call_id=1, data={'status':'success'})
                    ]

class Test(unittest.TestCase):
    
    def _ser(self, msg):
        cls = msg.__class__
        msg2 = cls.from_json(msg.as_json())
        self.assertEqual(msg.__dict__, msg2.__dict__)
        self.assertEqual(str(msg), str(msg2))
        msg2 = cls.from_binary(msg.as_binary())
        self.assertEqual(msg.__dict__, msg2.__dict__)
        self.assertEqual(str(msg), str(msg2))

    def test_messages(self):
        
        for msg in messages:
            print(msg)
            self._ser(msg)
            
    def test_deser(self):
        
        ms = [m.as_json() for m in messages[2:]] 
        dms = [msg_from_json(m) for m in ms]
        for i in range(len(dms)):
            self.assertEqual(str(dms[i]), str(messages[i+2]))
            
        ms = [m.as_binary() for m in messages[2:]] 
        dms = [msg_from_binary(m) for m in ms]
        for i in range(len(dms)):
            self.assertEqual(str(dms[i]), str(messages[i+2]))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()