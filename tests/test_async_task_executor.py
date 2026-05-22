import asyncio
import logging

import pytest

from src.collections.async_task_queue import AsyncTaskQueue
from src.executor.async_task_executor import AsyncTaskExecutor
from src.models.task import Task


class RecordingHandler:
    def __init__(self) -> None:
        self.entered = False
        self.closed = False
        self.handled_task_ids: list[int] = []

    async def __aenter__(self) -> "RecordingHandler":
        self.entered = True
        await asyncio.sleep(0)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> bool | None:
        self.closed = True
        await asyncio.sleep(0)
        return None

    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        assert self.entered
        await asyncio.sleep(0)
        self.handled_task_ids.append(task.id)


class HighPriorityHandler:
    def __init__(self) -> None:
        self.handled_task_ids: list[int] = []

    def can_handle(self, task: Task) -> bool:
        return task.priority == 5

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)
        self.handled_task_ids.append(task.id)


class FallbackHandler:
    def __init__(self) -> None:
        self.handled_task_ids: list[int] = []

    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)
        self.handled_task_ids.append(task.id)


class FailingHandler:
    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)
        raise RuntimeError("handler boom")


def test_async_executor_processes_tasks_and_manages_handler_context():
    handler = RecordingHandler()
    queue = AsyncTaskQueue(
        [
            Task(id=1, description="Первая задача", priority=3),
            Task(id=2, description="Вторая задача", priority=4),
        ]
    )

    async def scenario():
        async with AsyncTaskExecutor([handler], max_workers=2) as executor:
            results = await executor.run(queue)
            assert handler.entered
            assert not handler.closed
        return results

    results = asyncio.run(scenario())

    assert handler.closed
    assert sorted(handler.handled_task_ids) == [1, 2]
    assert all(result.success for result in results)
    assert {result.task.status for result in results} == {"done"}
    assert queue.empty()


def test_async_executor_selects_first_matching_handler():
    high_priority_handler = HighPriorityHandler()
    fallback_handler = FallbackHandler()
    queue = AsyncTaskQueue(
        [
            Task(id=1, description="Срочная задача", priority=5),
            Task(id=2, description="Обычная задача", priority=2),
        ]
    )

    async def scenario() -> None:
        async with AsyncTaskExecutor(
            [high_priority_handler, fallback_handler]
        ) as executor:
            await executor.run(queue)

    asyncio.run(scenario())

    assert high_priority_handler.handled_task_ids == [1]
    assert fallback_handler.handled_task_ids == [2]


def test_async_executor_logs_error_and_marks_task_failed(caplog):
    task = Task(id=10, description="Задача с ошибкой", priority=1)
    queue = AsyncTaskQueue([task])
    caplog.set_level(logging.ERROR)

    async def scenario():
        async with AsyncTaskExecutor([FailingHandler()]) as executor:
            return await executor.run(queue)

    results = asyncio.run(scenario())

    assert len(results) == 1
    assert not results[0].success
    assert results[0].error == "handler boom"
    assert task.status == "failed"
    assert "Ошибка при обработке задачи #10" in caplog.text


def test_async_executor_requires_context_manager():
    async def scenario() -> None:
        executor = AsyncTaskExecutor([RecordingHandler()])
        await executor.run(AsyncTaskQueue())

    with pytest.raises(RuntimeError):
        asyncio.run(scenario())


def test_async_executor_accepts_only_task_handler_protocol():
    with pytest.raises(TypeError):
        AsyncTaskExecutor([object()])


def test_async_executor_rejects_zero_max_workers():
    with pytest.raises(ValueError):
        AsyncTaskExecutor([RecordingHandler()], max_workers=0)


def test_async_executor_marks_task_failed_when_no_handler_found():
    class RejectAllHandler:
        def can_handle(self, task: Task) -> bool:
            return False

        async def handle(self, task: Task) -> None:
            pass

    task = Task(id=99, description="Без обработчика", priority=1)
    queue = AsyncTaskQueue([task])

    async def scenario():
        async with AsyncTaskExecutor([RejectAllHandler()]) as executor:
            return await executor.run(queue)

    results = asyncio.run(scenario())

    assert len(results) == 1
    assert not results[0].success
    assert results[0].handler_name is None
    assert task.status == "failed"


def test_async_executor_reraises_on_continue_on_error_false():
    task = Task(id=7, description="Сломанная задача", priority=2)
    queue = AsyncTaskQueue([task])

    async def scenario() -> None:
        async with AsyncTaskExecutor(
            [FailingHandler()], continue_on_error=False
        ) as executor:
            await executor.run(queue)

    with pytest.raises(RuntimeError, match="handler boom"):
        asyncio.run(scenario())
