ASEXOR
======

ASEXOR = ASynchronous EXecutOR

This module enables to execute defined tasks (processes) on remote machine. So nothing new - but this one 
is based on  [Python Asyncio](https://docs.python.org/3/library/asyncio.html) and is focusing on ease of 
use and low resources ovehead.

Intetion is to support non-critical long running tasks, initiated directly from client (Web Browser, CLI client 
or proxiing them from other backend (web server ...)). It was created for ebooks conversions, but any 
other similar tasks will work well. 

ASEXOR is Python 3.5+ only (due to new async and await keywords).

Key features
------------

- starts predefined tasks in separate processes
- tasks can be very easily defined - in simplest case task is small wrapper around existing program - just defining
  which options to provide and optionally how to parse results from stdout.
- multi-tasks - some tasks can generate and schedule a bunch of other tasks ( like convert all files in 
  given directory, etc.) 
- scheduling and execution of tasks -  queues tasks and then executes them with limits on maximum number
  of concurrently running tasks
- instant updates of tasks status - start of execution, error, results, progress (in case of multi-tasks)
- plugable authentication based on user token
- tasks prioritization and authorizations based on user roles ( acquired during authentication)
- support of several protocols:
  * WebSocket (JS or Python Client)
  * [WAMP](http://wamp-proto.org/) (JS or Python Client)
  * Raw Socket - TCP or Unix socket (Python Client)
  * HTTP Long Poll (POST+GET) - (JS or Python Client) 

Getting started
---------------
Examples how to use ASEXOR are in `test` directory. Assure you have Python 3.5 as default python 
interpreter or create virtual environment with Pyhton 3.5.

To play without installing `git clone --depth 1 https://github.com/izderadicka/asexor`

1. install requirements `pip install -r requirements.txt`
2. cd to `asexor/test/dummy_client`
3. [Install nodejs and npm](https://nodejs.org/en/download/), if not already installed
4. build  Javascript client
    ```
    npm install jspm -g #if not already installed
    jspm install
    jspm bundle app.js --inject
    ```

5. cd to `asexor/test` directory
6. run `PYTHONPATH=.. python dummy_backend.py -d` 
7. open `http://localhost:8484/index.html` in recent modern browser (FF, Chrome).
8. Select task (date or sleep) and run it

For more tests, demos look at README file in `test` directory.

Custom tasks
------------
Custom tasks are created as subclasses of `asexor.task.BaseSimpleTask` - you need to override:
- NAME, COMMAND, ARGS class properties
- `validate_args` method -validates parameters from RPC call and turns them into arguments that should be 
  passed to the command.  There is some basic support to define arguments in ARGS, but you can create them 
  in this method from scratch.
- `parse_result` - creates RPC return value - either by parsing output of the command or by other method.
- if task is to do something more complex, then just run some other program as subprocess, you can 
  overide `execute` method and do whatever is required 

Before custom tasks can be used they have to be registered by `asexor.task.load_tasks_from` function, 
which load all tasks from given module name. ( or `asexortask.register` to register single task).

For simple examples of tasks look at `test/tasks/simple_tasks.py`.

Multitasks
----------
You can create a task that creates multiple simple tasks, which will be scheduled subsequently 
(next task is scheduled after previous task is finished).
Check `asexor.task.BaseMultiTask` class (which takes list of task names and their arguments as input)

License
-------
GPL v.3 and newer




