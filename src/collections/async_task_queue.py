from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable

from src.collections.task_queue import TaskQueue
from src.models.task import Task


class AsyncTaskQueue:
    """Асинхронная очередь задач для обработки внутри event loop.

    Класс является продолжением синхронной `TaskQueue` из ЛР3: он может
    наполняться обычной коллекцией задач, но операции получения и добавления
    выполняются через `asyncio.Queue`, поэтому исполнитель может безопасно
    ожидать задачи без блокировки event loop.
    """

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        """Создаёт пустую асинхронную очередь и опционально наполняет её задачами."""
        self._queue: asyncio.Queue[Task] = asyncio.Queue()
        if tasks is not None:
            for task in tasks:
                self.enqueue_nowait(task)

    @classmethod
    def from_task_queue(cls, task_queue: TaskQueue) -> AsyncTaskQueue:
        """Создаёт асинхронную очередь из синхронной очереди ЛР3.

        Объекты `Task` не копируются: в новую очередь помещаются те же ссылки,
        что сохраняет единое состояние задачи между слоями приложения.
        """
        return cls(task_queue)

    def __len__(self) -> int:
        """Возвращает текущее количество задач в очереди."""
        return self._queue.qsize()

    def __bool__(self) -> bool:
        """Позволяет проверять наличие задач через обычное условие."""
        return not self.empty()

    def __aiter__(self) -> AsyncIterator[Task]:
        """Возвращает асинхронный итератор, который забирает задачи до опустошения."""
        return self._iterate_until_empty()

    def empty(self) -> bool:
        """Возвращает `True`, если в очереди нет ожидающих задач."""
        return self._queue.empty()

    async def enqueue(self, task: Task) -> None:
        """Асинхронно добавляет задачу в конец очереди."""
        self._validate_task(task)
        await self._queue.put(task)

    def enqueue_nowait(self, task: Task) -> None:
        """Добавляет задачу без ожидания, если очередь не ограничена по размеру."""
        self._validate_task(task)
        self._queue.put_nowait(task)

    async def dequeue(self) -> Task:
        """Асинхронно получает следующую задачу из очереди."""
        return await self._queue.get()

    def dequeue_nowait(self) -> Task:
        """Получает следующую задачу без ожидания.

        Если очередь пуста, пробрасывается стандартное `asyncio.QueueEmpty`.
        """
        return self._queue.get_nowait()

    def task_done(self) -> None:
        """Сообщает очереди, что ранее полученная задача обработана."""
        self._queue.task_done()

    async def join(self) -> None:
        """Ожидает завершения всех задач, полученных из очереди."""
        await self._queue.join()

    async def _iterate_until_empty(self) -> AsyncIterator[Task]:
        """Последовательно отдаёт задачи и отмечает их завершёнными после обхода."""
        while not self.empty():
            task = await self.dequeue()
            try:
                yield task
            finally:
                self.task_done()

    @staticmethod
    def _validate_task(task: Task) -> None:
        """Проверяет, что асинхронная очередь хранит только объекты `Task`."""
        if not isinstance(task, Task):
            raise TypeError("AsyncTaskQueue может хранить только объекты Task")
