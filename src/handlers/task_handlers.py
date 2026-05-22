from __future__ import annotations

import asyncio
from types import TracebackType

from src.models.task import Task


class DefaultTaskHandler:
    """Базовый обработчик, принимающий любую задачу.

    Класс реализует async context manager, имитируя открытие и закрытие
    внешнего ресурса без блокирующих операций.
    """

    def __init__(self, *, delay: float = 0) -> None:
        """Сохраняет искусственную асинхронную задержку обработки."""
        if delay < 0:
            raise ValueError("Задержка обработки не может быть отрицательной")
        self.delay = delay
        self.is_open = False

    async def __aenter__(self) -> DefaultTaskHandler:
        """Открывает ресурс обработчика."""
        await asyncio.sleep(0)
        self.is_open = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Закрывает ресурс обработчика."""
        await asyncio.sleep(0)
        self.is_open = False
        return None

    def can_handle(self, task: Task) -> bool:
        """Возвращает `True` для любой задачи."""
        return True

    async def handle(self, task: Task) -> None:
        """Асинхронно обрабатывает задачу без блокировки event loop."""
        if not self.is_open:
            raise RuntimeError("Обработчик должен быть открыт через async with")
        await asyncio.sleep(self.delay)


class PriorityTaskHandler:
    """Обработчик задач с приоритетом не ниже заданного порога."""

    def __init__(self, min_priority: int = 5) -> None:
        """Сохраняет минимальный приоритет задач, которые принимает обработчик."""
        if not 1 <= min_priority <= 5:
            raise ValueError("Минимальный приоритет должен быть в диапазоне от 1 до 5")
        self.min_priority = min_priority
        self.handled_task_ids: list[int] = []

    def can_handle(self, task: Task) -> bool:
        """Проверяет, подходит ли задача по приоритету."""
        return task.priority >= self.min_priority

    async def handle(self, task: Task) -> None:
        """Фиксирует обработку приоритетной задачи."""
        await asyncio.sleep(0)
        self.handled_task_ids.append(task.id)
