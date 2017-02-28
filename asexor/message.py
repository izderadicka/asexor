import inspect
from abc import ABC, abstractmethod

try:
    import ujson as json
except ImportError:
    import json
    
import cbor


class Message(ABC):
    
    @abstractmethod
    def as_data(self):
        pass
    
    @classmethod
    @abstractmethod
    def from_data(cls,data):
        pass
    
    def as_json(self):
        return json.dumps(self.as_data())
    
    def as_binary(self):
        return cbor.dumps(self.as_data())
    
    @classmethod
    def from_json(cls,string_data):
        return cls.from_data(json.loads(string_data))
    
    @classmethod
    def from_binary(cls,binary_data):
        return cls.from_data(cbor.loads(binary_data))
    
    def __str__(self):
        cls = self.__class__.__name__
        if hasattr(self, '__init__'):
            signature = inspect.signature(self.__init__)
            params = signature.parameters.keys()
            params = map(lambda n: '%s=%s'%(n, repr(getattr(self, n))), params)
            params=', '.join(params)
        else:
            params=''
        return '%s(%s)'%(cls,params)


class CallMessage(Message):
    
    def __init__(self, call_id, task_name, args=(), kwargs={}):
        assert(isinstance(args, (tuple, list)) and isinstance(kwargs, dict))
        self.call_id = call_id
        self.task_name = task_name
        
        self.args = args
        self.kwargs = kwargs
        
    def as_data(self):
        payload = {}
        if self.args:
            payload['args'] = self.args
        if self.kwargs:
            payload['kwargs'] = self.kwargs
            
        return (self.call_id, self.task_name, payload)
    
    @classmethod
    def from_data(cls, data):
        try:
            call_id, task_name, payload = data
            args = payload.get('args') or ()
            kwargs = payload.get('kwargs') or {}
            return CallMessage(call_id, task_name, args, kwargs)
        except Exception as e:
            try:
                call_id = data[0]
            except:
                pass
            else:
                e.call_id = call_id
            raise e
    
MSG_TYPE_REPLY = 'r'
MSG_TYPE_UPDATE = 'm';
MSG_TYPE_ERROR = 'e'
            

class ReplyMessage(Message):
    TYPE = MSG_TYPE_REPLY
    def __init__(self, call_id, task_id):
        self.call_id = call_id
        self.task_id = task_id
        
    def as_data(self):
        return [self.TYPE, self.call_id, self.task_id]
    
    @classmethod
    def from_data(cls, data):
        _type, call_id, task_id = data
        return ReplyMessage(call_id, task_id)
    
class ErrorMessage(Message):
    TYPE = MSG_TYPE_ERROR
    
    def __init__(self, call_id, error, error_stack=None):
        self.call_id = call_id
        self.error = error
        self.error_stack = error_stack
        
    def as_data(self):
        return self.TYPE, self.call_id, self.error, self.error_stack
    
    @classmethod
    def from_data(cls, data):
        _type, call_id, error, error_stack = data
        return ErrorMessage(call_id, error, error_stack)
    

    
class UpdateMessage(Message):
    TYPE = MSG_TYPE_UPDATE
    
    def __init__(self, call_id, data):
        self.call_id = call_id
        self.data = data
        
    def as_data(self):
        return self.TYPE, self.call_id, self.data
    
    @classmethod
    def from_data(cls, d):
        _type, call_id, data = d
        return UpdateMessage(call_id, data)

MSG_CLASSES= {cls.TYPE:cls for cls in (ErrorMessage, ReplyMessage, UpdateMessage )}    

def _msg_from_data(data):
    try:
        cls = MSG_CLASSES[data[0]]
    except KeyError:
        raise ValueError('Invalid message type')
    return cls.from_data(data)

def msg_from_json(data):
    data = json.loads(data)
    return _msg_from_data(data)

def msg_from_binary(data):
    data =  cbor.loads(data)
    return _msg_from_data(data)

    