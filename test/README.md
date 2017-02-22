This directory contains several tests for ASEXOR package

Unit Tests
----------

Install pytest and run
`PYTHONPATH=.. py.test .

Demo WebSocket (aiohttp) backend, browser client (Javascript) and Python client
-------------------------------------------------------------------------------
Example how to use is in `test` directory. Assure you have Python 3.5 as default python interpreter or create virtual environment with Pyhton 3.5.
1. install requirements `pip install -r requirements.txt`
2. cd to `test` directory
3. run `PYTHONPATH=.. python dummy_backend.py -d`
4. open `http://localhost:8484` in recent modern browser (FF, Chrome).
5. Select task and run 
6. try also python client `PYTHONPATH=.. python dummy_client.py -n 10  -d user_name` in other terminal window




Demo WAMP backend, browser client (Javascript) and Python client
----------------------------------------------------------------

Example how to use is in `test` directory. Assure you have Python 3.5 as default python interpreter or create virtual environment with Pyhton 3.5.
1. install requirements `pip install -r requirements.txt`
2. cd to `test` directory
3. run `crossbar start`
4. run `PYTHONPATH=.. python dummy_backend.py -d --use-wamp` in other terminal window
5. open `wamp_client.html` in recent modern browser (FF, Chrome).
6. Select task and run 
7. try also python client `PYTHONPATH=.. python dummy_client.py -d -n 10  --use-wamp user_name` in other terminal window

