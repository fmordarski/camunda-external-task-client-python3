import logging
from concurrent.futures.thread import ThreadPoolExecutor

from frozendict import frozendict

from camunda.external_task.external_task import ExternalTask
from camunda.external_task.external_task_worker import ExternalTaskWorker
from camunda.utils.log_utils import log_with_context

logger = logging.getLogger(__name__)

default_config = frozendict({
    "maxTasks": 1,
    "lockDuration": 10000,
    "asyncResponseTimeout": 30000,
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 30,
    "isDebug": True,
})


def generic_task_handler(task: ExternalTask):
    log_context = frozendict({"WORKER_ID": task.get_worker_id(), "TASK_ID": task.get_task_id(),
                              "TOPIC": task.get_topic_name()})
    log_with_context("executing generic_task_handler", log_context)
    outcome = task.get_variable('outcome')

    if "bpmn_error" in outcome:
        return task.bpmn_error("BPMN_ERROR", "BPMN Error occurred")
    elif "success" in outcome:
        return task.complete({})
    else:
        return task.failure("Task failed", "Task failed", 0, default_config.get("retryTimeout"))


def main():
    configure_logging()
    topics = [("STEP_1", generic_task_handler),
              ]
    executor = ThreadPoolExecutor(max_workers=len(topics))
    for index, topic_handler in enumerate(topics):
        topic = topic_handler[0]
        handler_func = topic_handler[1]
        executor.submit(ExternalTaskWorker(worker_id=index, config=default_config).subscribe, topic, handler_func)


def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.StreamHandler()])


if __name__ == '__main__':
    main()
