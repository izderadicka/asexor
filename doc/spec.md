Asexor = Asynchronous Executor
==============================

- based on Asyncio
- WAMP interface to initiate runs and receive notifications
- Runs any configured program and returns results  
- task preprocess and post process as coroutiness
- params arguments positional and named
- Integrated with authentication / authorization - configurable
- Priority of tasks connected with users roles - configurable
- Maximum number of concurrent processes
- Process timeout
- Parsing process results from stdout
- Configurable tasks - processes
- Tasks queue - maximum number of tasks
- Cancel tasks from queue?
- publish task progress -  started, done (with result), ?queue position?
- query
  - task status,  all my tasks ...
  - general server status - number of tasks - statistics etc.
- Configuration
- KISS

Message flow
------------
[RPC]
  [Preprocess] task name, params -> params
  -> Request Task - task name, params, (user name, role ...)  
  <- task_id or error, queue_size?
[MSG] # sen only to user?
<- task started
[Post process] or [Report Error]
  [Parse stdio] and [Parse stderr]
<- task finished  - returned result
