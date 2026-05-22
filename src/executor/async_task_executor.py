from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from contextlib import AsyncExitStack
from dataclasses import dataclass
from types import TracebackType

from src.collections.async_task_queue import AsyncTaskQueue
from src.contracts.task_handler import ManagedTaskHandler, TaskHandler
from src.models.task import Task


@dataclass(frozen=True)
class TaskExecutionResult:
    """Итог обработки одной задачи асинхронным исполнителем."""

    task: Task
    handler_name: str | None
    success: bool
    error: str | None = None


class AsyncTaskExecutor:
    """Асинхронный исполнитель задач с расширяемыми обработчиками.

    Исполнитель не знает конкретных классов обработчиков. Он работает только
    через `TaskHandler`, поэтому новые стратегии обработки добавляются без
    изменения очереди или самого механизма исполнения.
    """

    def __init__(
        self,
        handlers: Iterable[TaskHandler],
        *,
        max_workers: int = 1,
        continue_on_error: bool = True,
        logger: logging.Logger | None = None,
    ) -> None:
        """Создаёт исполнитель и проверяет обработчики на соответствие контракту."""
        if max_workers < 1:
            raise ValueError("Количество воркеров должно быть положительным")

        self.handlers = list(handlers)
        for handler in self.handlers:
            if not isinstance(handler, TaskHandler):
                raise TypeError(
                    f"{type(handler).__name__} не реализует контракт TaskHandler"
                )

        self.max_workers = max_workers
        self.continue_on_error = continue_on_error
        self.logger = logger or logging.getLogger(__name__)
        self._exit_stack: AsyncExitStack | None = None
        self._is_running = False

    async def __aenter__(self) -> AsyncTaskExecutor:
        """Открывает ресурсы управляемых обработчиков перед обработкой задач."""
        self._exit_stack = AsyncExitStack()
        for handler in self.handlers:
            if isinstance(handler, ManagedTaskHandler):
                await self._exit_stack.enter_async_context(handler)

        self._is_running = True
        self.logger.info("Асинхронный исполнитель задач запущен")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Освобождает ресурсы обработчиков после завершения обработки."""
        try:
            if self._exit_stack is not None:
                await self._exit_stack.__aexit__(exc_type, exc, traceback)
        finally:
            self._exit_stack = None
            self._is_running = False
            self.logger.info("Асинхронный исполнитель задач остановлен")
        return None

    async def run(self, queue: AsyncTaskQueue) -> list[TaskExecutionResult]:
        """Обрабатывает все задачи из очереди и возвращает результаты.

        Метод должен вызываться внутри `async with AsyncTaskExecutor(...)`,
        чтобы обработчики, владеющие ресурсами, были открыты и закрыты
        централизованно.
        """
        if not self._is_running:
            raise RuntimeError("AsyncTaskExecutor нужно использовать через async with")

        results: list[TaskExecutionResult] = []
        results_lock = asyncio.Lock()

        async def worker() -> None:
            while True:
                try:
                    task = queue.dequeue_nowait()
                except asyncio.QueueEmpty:
                    return

                try:
                    result = await self._process_task(task)
                finally:
                    queue.task_done()

                async with results_lock:
                    results.append(result)

        worker_count = min(self.max_workers, max(len(queue), 1))
        await asyncio.gather(*(worker() for _ in range(worker_count)))
        await queue.join()
        return results

    async def _process_task(self, task: Task) -> TaskExecutionResult:
        """Находит обработчик, запускает задачу и централизованно фиксирует итог."""
        handler = self._find_handler(task)
        if handler is None:
            task.status = "failed"
            message = f"Для задачи #{task.id} не найден подходящий обработчик"
            self.logger.error(message)
            return TaskExecutionResult(
                task=task,
                handler_name=None,
                success=False,
                error=message,
            )

        handler_name = type(handler).__name__
        task.status = "in_progress"
        self.logger.info("Задача #%s передана обработчику %s", task.id, handler_name)

        try:
            await handler.handle(task)
        except Exception as error:
            task.status = "failed"
            self.logger.exception(
                "Ошибка при обработке задачи #%s обработчиком %s",
                task.id,
                handler_name,
            )
            if not self.continue_on_error:
                raise
            return TaskExecutionResult(
                task=task,
                handler_name=handler_name,
                success=False,
                error=str(error),
            )

        task.status = "done"
        self.logger.info("Задача #%s успешно обработана", task.id)
        return TaskExecutionResult(
            task=task,
            handler_name=handler_name,
            success=True,
        )

    def _find_handler(self, task: Task) -> TaskHandler | None:
        """Возвращает первый обработчик, готовый принять задачу."""
        for handler in self.handlers:
            if handler.can_handle(task):
                return handler
        return None
