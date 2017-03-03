This directory contains several tests for ASEXOR package

Unit Tests
----------

Install pytest and run
`PYTHONPATH=.. py.test .

Test dummy application
-------------------------------------------------------------------------------
Dummy application is consisting of:
- dummy backend, which can run two tasks (standard unix commands) - date and sleep
- javascript client -  user can interactivelly run of of these tasks
- python client - send n of tasks randomly chosen between date and sleep
 
Dummy application is in `test` directory. 
Assure you have Python 3.5 as default python interpreter or create virtual environment with Pyhton 3.5.
1. install requirements `pip install -r requirements.txt`
2. cd to `test` directory
3. run `PYTHONPATH=.. python dummy_backend.py -d`
4. open `http://localhost:8484/index.html` in recent modern browser (FF, Chrome).
5. Select task and run 
6. try also python client `PYTHONPATH=.. python dummy_client.py -n 10  -d user_name` in other terminal window



Other tests
-----------
To run mulptiple clients in parallel (and measure time):
```
time ( for n in {1..100}; do  { python dummy_client.py  ivan  -n 10  --use-raw & }  ; done ; wait )
```

