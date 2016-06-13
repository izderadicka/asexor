ASEXOR
======

ASEXOR = ASynchronous EXecutOR

This module enables to execute defined tasks (processes) on remote machine. So nothing new - but this one 
is based on two relatively new technologies -  [Python Asyncio](https://docs.python.org/3/library/asyncio.html) and [WAMP](http://wamp-proto.org/). 

So it's well suited for running tasks for web based applications (for instance file conversions). 

Python 3.5 only (due to new async and await keywords).

Getting started
---------------
Example how to use is in `test` directory. Assure you have Python 3.5 as default python interpreter or create virtual environment with Pyhton 3.5.
1. install requirements `pip install -r requirements.txt`
2. cd to `test` directory
3. run `crossbar start`
4. run `python dummy_server.py`
5. open `dummy_client.html` in recent modern browser (FF, Chrome).
6. Select task and run 
7. try also python client `python dummy_client -n 10  user_name`

Custom tasks
------------
Custom tasks are created as subclasses of `task.BaseTask` - you need to override:
- NAME, COMMAND, ARGS class properties
- `validate_args` method -validates parameters from RPC call and turns them into arguments that should be passed to the command.  There is some basic support to define arguments in ARGS, but you can create them in this method from scratch.
- `parse_result` - creates RPC return value - either by parsing output of the command or by other method.

Before custom tasks can be used they have to be registered by `task.load_tasks_form` function, which load all tasks from given module name. ( or `task.register` to register single task).

For simple examples of tasks look at `test/tasks/simple_tasks.py`.



