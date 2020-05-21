# camunda-external-task-client-python
![camunda-external-task-client-python](https://github.com/yogeshrnaik/camunda-external-task-client-python/workflows/camunda-external-task-client-python/badge.svg?branch=master)

This repository contains Camunda External Task Client written in Pyhon3.


Implement your [BPMN Service Task](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/) in Python3.

> Python >= v3.x is required

## Installing
Add following line to `requirements.txt` of your Python project.

`git+https://github.com/trustfactors/camunda-external-task-client-python.git/#egg=camunda-external-task-client-python`


## Usage

1.  Make sure to have [Camunda](https://camunda.com/download/) running.
2.  Create a simple process model with an External Service Task and define the topic as 'topicName'.
3.  Deploy the process to the Camunda BPM engine.
4.  In your Python code:

```python
import time
import asyncio
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

# configuration for the Client
default_config = {
    "maxTasks": 1,
    "lockDuration": 10000,
    "asyncResponseTimeout": 5000,
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 30
}

async def handle_task(task: ExternalTask) -> TaskResult:
    """
    This task handler you need to implement with your business logic.
    After completion of business logic call either task.complete() or task.failure() or task.bpmn_error() 
    to report status of task to Camunda
    """
    # add your business logic here
    # ...
    
    # mark task either complete/failure/bpmnError based on outcome of your business logic
    failure, bpmn_error = random_true(), random_true() # this code simulate random failure
    if failure:
        # this marks task as failed in Camunda
        return task.failure(error_message="task failed",  error_details="failed task details", 
                            max_retries=3, retry_timeout=5000)
    elif bpmn_error:
        return task.bpmn_error(error_cide="BPMN_ERROR_CODE")
    
    # pass any output variables you may want to send to Camunda as dictionary to complete()
    return task.complete({"var1": 1, "var2": "value"}) 

def random_true():
    current_milli_time = int(round(time.time() * 1000))
    return current_milli_time % 2 == 0

if __name__ == '__main__':
    asyncio.run(ExternalTaskWorker(config=default_config).subscribe("topicName", handle_task))
```

## About External Tasks

External Tasks are service tasks whose execution differs particularly from the execution of other service tasks (e.g. Human Tasks).
The execution works in a way that units of work are polled from the engine before being completed.

**camunda-external-task-client-python** allows you to create easily such client in Python3.

## Features
### [Fetch and Lock](https://docs.camunda.org/manual/latest/reference/rest/external-task/fetch/)

Done through [polling](/docs/Client.md#about-polling).

### [Complete](https://docs.camunda.org/manual/latest/reference/rest/external-task/post-complete/)
```python
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
async def handle_task(task: ExternalTask) -> TaskResult:
    # add your business logic here
    
    # Complete the task
    # pass any output variables you may want to send to Camunda as dictionary to complete()
    return task.complete({"var1": 1, "var2": "value"})

ExternalTaskWorker().subscribe("topicName", handle_task)
```

### [Handle Failure](https://docs.camunda.org/manual/latest/reference/rest/external-task/post-failure/)
```python
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
async def handle_task(task: ExternalTask) -> TaskResult:
    # add your business logic here
    
    # Handle task Failure
    return task.failure(error_message="task failed",  error_details="failed task details", 
                        max_retries=3, retry_timeout=5000)
    # This client/worker uses max_retries if no retries are previously set in the task
    # if retries are previously set then it just decrements that count by one before reporting failure to Camunda
    # when retries are zero, Camunda creates an incident which then manually needs to be looked into on Camunda Cockpit            

ExternalTaskWorker().subscribe("topicName", handle_task)
```

### [Handle BPMN Error](https://docs.camunda.org/manual/latest/reference/rest/external-task/post-bpmn-error/)
```python
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
async def handle_task(task: ExternalTask) -> TaskResult:
    # add your business logic here
    
    # Handle a BPMN Failure
    return task.bpmn_error(error_code="BPMN_ERROR")

ExternalTaskWorker().subscribe("topicName", handle_task)
```

### Access Local Task Variables
```python
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
async def handle_task(task: ExternalTask) -> TaskResult:
    # add your business logic here
    # get the process variable 'score'
    score = task.get_local_variable("score")
    if int(score) >= 100:
        return task.complete(...)
    else:
        return task.failure(...)        

ExternalTaskWorker().subscribe("topicName", handle_task)
```

## License
The source files in this repository are made available under the [Apache License Version 2.0](./LICENSE).
