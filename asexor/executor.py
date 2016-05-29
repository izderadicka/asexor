import sys
import asyncio
from datetime import datetime
import os.path
import logging
log = logging.getLogger('backend')

from autobahn.asyncio.wamp import ApplicationSession
from asexor.runner import ApplicationRunnerRawSocket


class MyComponent(ApplicationSession):

    async def onJoin(self, details):
        # a remote procedure; see frontend.py for a Python front-end
        # that calls this. Any language with WAMP bindings can now call
        # this procedure if its connected to the same router and realm.
        def add2(x, y):
            log.debug('add2 called with %s %s', x, y)
            return x + y
        await self.register(add2, u'com.myapp.add2')

        # publish an event every second. The event payloads can be
        # anything JSON- and msgpack- serializable
        while True:
            self.publish(u'com.myapp.hello', 'Hello, world! Time is %s' % datetime.utcnow())
            log.debug('Published msg')
            await asyncio.sleep(1)


if __name__ == '__main__':
    level = 'info'
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        level = 'debug'
    path = os.path.join(os.path.dirname(__file__), '.crossbar/socket1')
    runner = ApplicationRunnerRawSocket(
        path,
        u"realm1",
    )
    runner.run(MyComponent, logging_level=level)
