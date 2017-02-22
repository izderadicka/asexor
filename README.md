ASEXOR
======

ASEXOR = ASynchronous EXecutOR

This module enables to execute defined tasks (processes) on remote machine. So nothing new - but this one 
is based on two relatively new technologies -  [Python Asyncio](https://docs.python.org/3/library/asyncio.html) and [WAMP](http://wamp-proto.org/). 

So it's well suited for running tasks for web based applications (for instance file conversions). 

Python 3.5 only (due to new async and await keywords).

WARNING - API IS NOW UNDER REFACTORING.

Getting started
---------------
Example how to use is in `test` directory. Assure you have Python 3.5 as default python 
interpreter or create virtual environment with Pyhton 3.5.
To play without installing `git clone https://github.com/izderadicka/asexor`
1. install requirements `pip install -r requirements.txt` (optional if not installed with setup.py)
2. cd to `asexor/test` directory
3. run `PYTHONPATH=.. python dummy_backend.py -d` 
4. open `http://localhost:8484` in recent modern browser (FF, Chrome).
5. Select task and run 
6. try also python client `PYTHONPATH=.. python dummy_client.py -n 10  -d user_name` in other terminal window

for more tests, demos look at README file in test directory.

Custom tasks
------------
Custom tasks are created as subclasses of `asexor.task.BaseSimpleTask` - you need to override:
- NAME, COMMAND, ARGS class properties
- `validate_args` method -validates parameters from RPC call and turns them into arguments that should be passed to the command.  There is some basic support to define arguments in ARGS, but you can create them in this method from scratch.
- `parse_result` - creates RPC return value - either by parsing output of the command or by other method.
- if task is to do something more complex, then just run some other program as subprocess, you can overide `execute` method and do whatever is required 

Before custom tasks can be used they have to be registered by `task.load_tasks_form` function, which load all tasks from given module name. ( or `task.register` to register single task).

For simple examples of tasks look at `test/tasks/simple_tasks.py`.

Multitasks
----------
You can create a task that creates multiple simple tasks, which will be scheduled subsequently 
(next task is scheduled after previous task is finished).
Check `asexor.task.BaseMultiTask` class (which takes list of task names and their arguments as input)



