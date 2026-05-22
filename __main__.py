import asyncio
import logging
import sys

from src.collections.async_task_queue import AsyncTaskQueue
from src.collections.task_queue import TaskQueue
from src.contracts.task_source import TaskSource
from src.contracts.task_handler import TaskHandler
from src.executor.async_task_executor import AsyncTaskExecutor
from src.handlers.task_handlers import DefaultTaskHandler, PriorityTaskHandler
from src.models.task import Task
from src.receiver.task_receiver import TaskReceiver

from src.sources.generator_source import GeneratorSource
from src.sources.file_source import FileSource
from src.sources.api_stub_source import APIStubSource


def load_demo_tasks() -> list[Task]:
    """Загружает демонстрационные задачи из всех учебных источников.

    Функция последовательно обращается к генератору, JSON-файлу и
    API-заглушке, после чего возвращает общий список задач.
    """
    receiver = TaskReceiver()
    sources: list[TaskSource] = [
        GeneratorSource(3),
        FileSource("data/tasks.json"),
        APIStubSource(),
    ]
    tasks: list[Task] = []
    for source in sources:
        print(f"\nSource: {source.__class__.__name__}")
        received_tasks = receiver.receive(source)
        for task in received_tasks:
            print(task)
        tasks.extend(received_tasks)
    return tasks


async def run_async_processing(tasks: list[Task]) -> None:
    """Запускает асинхронную обработку задач из очереди ЛР3."""
    task_queue = TaskQueue(tasks)
    async_queue = AsyncTaskQueue.from_task_queue(task_queue)
    handlers: list[TaskHandler] = [
        PriorityTaskHandler(min_priority=5),
        DefaultTaskHandler(),
    ]

    async with AsyncTaskExecutor(handlers, max_workers=2) as executor:
        results = await executor.run(async_queue)

    print("\nAsync processing results:")
    for result in results:
        status = "ok" if result.success else f"error: {result.error}"
        print(f"Task #{result.task.id}: {status}")


def main() -> None:
    """Запускает демонстрационный сценарий ЛР4 поверх кода ЛР3."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(message)s",
        stream=sys.stdout,
    )
    tasks = load_demo_tasks()
    asyncio.run(run_async_processing(tasks))


if __name__ == "__main__":
    main()
