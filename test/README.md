This directory contains several tests for ASEXOR package

Unit Tests
----------

Install pytest and run
```
cd test
export PYTHONPATH=.. 
py.test
py.test aiohttp_test*
```

Test dummy application
-------------------------------------------------------------------------------
Dummy application is consisting of:
- dummy backend, which can run two tasks (standard unix commands) - date and sleep
- javascript client -  user can interactivelly run of of these tasks
- python client - send n of tasks randomly chosen between date and sleep

By default dummy_backend and dummy_client support WebSocket protocol. U
 
Dummy application is in `test` directory. 
Assure you have Python 3.5 as default python interpreter or create virtual environment with Pyhton 3.5.
1. install requirements `pip install -r requirements.txt`
2. build  Javascript client (assuming nodejs and npm is already installed on your computer:
```
# cd to test/dummy_client directory
npm install jspm -g #if not already installed
jspm install
jspm bundle app.js --inject
```
3. cd to `test` directory
4. run `PYTHONPATH=.. python dummy_backend.py --use-raw --use-long-poll -d`. 
    Optionally you can also add `--use-wamp` option if crossbar WAMP router is running.
5. open `http://localhost:8484/index.html` in recent modern browser (FF, Chrome).
6. Select task and run 
7. try also python client `PYTHONPATH=.. python dummy_client.py -n 10  -d user_name` in other terminal window.
   You can also try other protocols with these options: `--use-raw` `--use-long-poll` `--use-wamp`
   

Other tests
-----------
To run mulptiple clients in parallel (and measure time):
```
time ( for n in {1..100}; do  { python dummy_client.py  ivan  -n 10  --use-raw & }  ; done ; wait )
```

`delegating_client` - client for raw socket protocol, that can delagate tasks for other users
`flood_client` - foold backend with many long running tasks