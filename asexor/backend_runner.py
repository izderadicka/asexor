import asyncio
from asexor.tqueue import TasksQueue
from asexor.config import Config
from copy import copy
import logging

logger = logging.getLogger('backend_runner')


class Runner:
    
    def __init__(self, protocols, loop=None):
        """ 
        Runs given backend protocols
        
        :param protocols: - list of protocols to runs - each protocol is tuple (ProtoClass, ProtoParams)
        """
        
        self.loop = loop or asyncio.get_event_loop()
        assert isinstance(protocols, (list, tuple))
        self.protocols = []
        
        for cls, params in protocols:
            kwargs = copy(params)
            self.protocols.append(cls(self.loop, **kwargs))
            
            
    def run(self):
        tasks_queue= TasksQueue(concurrent=Config.CONCURRENT_TASKS,
                                queue_size=Config.TASKS_QUEUE_MAX_SIZE)
        
        for p in self.protocols:
            logger.debug('Starting protocol %s', p)
            self.loop.run_until_complete(p.start(tasks_queue))
            
        tq = self.loop.create_task(tasks_queue.run_tasks())
        logger.debug('Tasks queue started')
        async def stop_tasks_queue():
            tasks_queue.stop()
            tq.cancel()
            try:
                await asyncio.wait_for(tq, 10)
            except asyncio.TimeoutError:
                logger.error('Tasks queue not terminated in given time')
            except asyncio.CancelledError:
                pass
        
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception:
            logger.exception('Error in main loop')
        finally:
            for p in self.protocols:
                logger.debug('Stoping protocol %s', p)
                self.loop.run_until_complete(p.stop())
                
            self.loop.run_until_complete(stop_tasks_queue())
            
            self.loop.close()
            
            
        
# Mozna se hodi?
#         try:
#             loop.add_signal_handler(signal.SIGTERM, loop.stop)
#         except NotImplementedError:
#             # signals are not available on Windows
#             pass
# 
#         def handle_error(loop, context):
#             log.error('Application Error: %s', context)
#             if 'exception' in context and context['exception']:
#                 import traceback
#                 e = context['exception']
#                 tb='\n'.join(traceback.format_tb(e.__traceback__)) if hasattr(e, '__traceback__') else ''
#                 logging.error('Exception : %s \n %s', repr(e), tb)
#             loop.stop()
# 
#         loop.set_exception_handler(handle_error)            