import asyncio

import pytest

from src.collections.async_task_queue import AsyncTaskQueue
from src.collections.task_queue import TaskQueue
from src.models.task import Task


def make_tasks() -> list[Task]:
    return [
        Task(id=1, description="Проверить входящие события", priority=5),
        Task(id=2, description="Обновить витрину отчётов", priority=2),
    ]


def test_async_task_queue_preserves_fifo_order():
    async def scenario() -> list[int]:
        queue = AsyncTaskQueue()
        for task in make_tasks():
            await queue.enqueue(task)

        first_task = await queue.dequeue()
        queue.task_done()
        second_task = await queue.dequeue()
        queue.task_done()
        await queue.join()
        return [first_task.id, second_task.id]

    assert asyncio.run(scenario()) == [1, 2]


def test_async_task_queue_can_be_created_from_task_queue_without_copying():
    tasks = make_tasks()
    sync_queue = TaskQueue(tasks)
    async_queue = AsyncTaskQueue.from_task_queue(sync_queue)

    async def scenario() -> Task:
        first_task = await async_queue.dequeue()
        async_queue.task_done()
        second_task = await async_queue.dequeue()
        async_queue.task_done()
        assert second_task is tasks[1]
        await async_queue.join()
        return first_task

    assert asyncio.run(scenario()) is tasks[0]


def test_async_task_queue_supports_async_iteration_until_empty():
    async def scenario() -> tuple[list[int], bool]:
        queue = AsyncTaskQueue(make_tasks())
        ids: list[int] = []

        async for task in queue:
            ids.append(task.id)

        await queue.join()
        return ids, queue.empty()

    assert asyncio.run(scenario()) == ([1, 2], True)


def test_async_task_queue_accepts_only_task_instances():
    with pytest.raises(TypeError):
        AsyncTaskQueue(["not a task"])
