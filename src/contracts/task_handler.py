from __future__ import annotations

from types import TracebackType
from typing import Protocol, runtime_checkable

from src.models.task import Task


@runtime_checkable
class TaskHandler(Protocol):
    """Контракт асинхронного обработчика задач.

    Обработчики не обязаны наследоваться от общего базового класса. Достаточно
    структурно поддержать методы `can_handle` и `handle`, чтобы исполнитель мог
    выбрать подходящий обработчик и дождаться результата через `await`.
    """

    def can_handle(self, task: Task) -> bool:
        """Возвращает `True`, если обработчик умеет обработать задачу."""
        ...

    async def handle(self, task: Task) -> None:
        """Асинхронно обрабатывает задачу."""
        ...


@runtime_checkable
class ManagedTaskHandler(TaskHandler, Protocol):
    """Расширенный контракт обработчика, управляющего ресурсами через `async with`."""

    async def __aenter__(self) -> ManagedTaskHandler:
        """Открывает ресурсы обработчика перед запуском исполнителя."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Освобождает ресурсы обработчика после завершения работы."""
        ...
