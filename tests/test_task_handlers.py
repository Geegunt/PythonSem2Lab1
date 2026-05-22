import asyncio

import pytest

from src.handlers.task_handlers import DefaultTaskHandler, PriorityTaskHandler
from src.models.task import Task


def make_task(priority: int = 3) -> Task:
    return Task(id=1, description="Тестовая задача", priority=priority)


# --- DefaultTaskHandler ---


def test_default_handler_rejects_negative_delay():
    with pytest.raises(ValueError):
        DefaultTaskHandler(delay=-1)


def test_default_handler_can_handle_any_task():
    handler = DefaultTaskHandler()
    assert handler.can_handle(make_task(priority=1))
    assert handler.can_handle(make_task(priority=5))


def test_default_handler_raises_when_not_opened():
    async def scenario() -> None:
        handler = DefaultTaskHandler()
        await handler.handle(make_task())

    with pytest.raises(RuntimeError):
        asyncio.run(scenario())


def test_default_handler_context_manager_opens_and_closes():
    async def scenario() -> tuple[bool, bool]:
        handler = DefaultTaskHandler()
        async with handler:
            is_open = handler.is_open
        return is_open, handler.is_open

    open_inside, open_after = asyncio.run(scenario())
    assert open_inside is True
    assert open_after is False


def test_default_handler_handle_completes_inside_context():
    async def scenario() -> None:
        handler = DefaultTaskHandler()
        async with handler:
            await handler.handle(make_task())

    asyncio.run(scenario())


def test_default_handler_handle_with_delay():
    async def scenario() -> None:
        handler = DefaultTaskHandler(delay=0.01)
        async with handler:
            await handler.handle(make_task())

    asyncio.run(scenario())


# --- PriorityTaskHandler ---


def test_priority_handler_rejects_zero_priority():
    with pytest.raises(ValueError):
        PriorityTaskHandler(min_priority=0)


def test_priority_handler_rejects_priority_above_five():
    with pytest.raises(ValueError):
        PriorityTaskHandler(min_priority=6)


def test_priority_handler_can_handle_at_threshold():
    handler = PriorityTaskHandler(min_priority=3)
    assert handler.can_handle(make_task(priority=3))
    assert handler.can_handle(make_task(priority=5))


def test_priority_handler_cannot_handle_below_threshold():
    handler = PriorityTaskHandler(min_priority=4)
    assert not handler.can_handle(make_task(priority=3))
    assert not handler.can_handle(make_task(priority=1))


def test_priority_handler_records_handled_task_ids():
    async def scenario() -> list[int]:
        handler = PriorityTaskHandler(min_priority=1)
        task = make_task(priority=3)
        await handler.handle(task)
        return handler.handled_task_ids

    assert asyncio.run(scenario()) == [1]
