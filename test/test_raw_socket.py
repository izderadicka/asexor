'''
Created on Mar 1, 2017

@author: ivan
'''
import unittest
from unittest.mock import Mock, call
from asexor.raw_socket import PrefixProtocol


class Test(unittest.TestCase):

    
    def test_prefix(self):
        p = PrefixProtocol()
        transport = Mock()
        receiver = Mock()
        p.frame_received = receiver
        p.connection_made(transport)
        small_msg = b'\x00\x00\x00\x04abcd'
        p.data_received(small_msg)
        receiver.assert_called_once_with(b'abcd')
        self.assertEqual(len(p._buffer), 0)

        p.send(b'abcd')

        # print(transport.write.call_args_list)
        transport.write.assert_has_calls([call(b'\x00\x00\x00\x04'), call(b'abcd')])

        transport.reset_mock()
        receiver.reset_mock()

        big_msg = b'\x00\x00\x00\x0C' + b'0123456789AB'

        p.data_received(big_msg[0:2])
        self.assertFalse(receiver.called)

        p.data_received(big_msg[2:6])
        self.assertFalse(receiver.called)

        p.data_received(big_msg[6:11])
        self.assertFalse(receiver.called)

        p.data_received(big_msg[11:16])
        receiver.assert_called_once_with(b'0123456789AB')

        transport.reset_mock()
        receiver.reset_mock()

        two_messages = b'\x00\x00\x00\x04' + b'abcd' + b'\x00\x00\x00\x05' + b'12345' + b'\x00'
        p.data_received(two_messages)
        receiver.assert_has_calls([call(b'abcd'), call(b'12345')])
        self.assertEqual(p._buffer, b'\x00')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()