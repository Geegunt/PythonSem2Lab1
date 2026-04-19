from __future__ import annotations

from collections.abc import Iterable, Iterator

from src.models.task import Task


class TaskQueue:
    """Пользовательская коллекция задач с повторяемой итерацией.

    Очередь переиспользует готовую модель `Task`: она не создаёт новые
    задачи и не меняет их состояние, а только хранит ссылки на объекты.
    Фильтры реализованы как генераторы, поэтому задачи отбираются лениво
    во время обхода.
    """

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        """Создаёт очередь и, если переданы задачи, добавляет их по порядку."""
        self._tasks: list[Task] = []
        if tasks is not None:
            self.extend(tasks)

    def __iter__(self) -> Iterator[Task]:
        """Возвращает новый итератор для каждого обхода очереди."""
        for task in self._tasks:
            yield task

    def __len__(self) -> int:
        """Возвращает количество задач в очереди."""
        return len(self._tasks)

    def __bool__(self) -> bool:
        """Позволяет проверять очередь в условии как обычную коллекцию."""
        return bool(self._tasks)

    def enqueue(self, task: Task) -> None:
        """Добавляет задачу в конец очереди."""
        self._validate_task(task)
        self._tasks.append(task)

    def extend(self, tasks: Iterable[Task]) -> None:
        """Добавляет в очередь все задачи из переданного итерируемого объекта."""
        for task in tasks:
            self.enqueue(task)

    def dequeue(self) -> Task:
        """Удаляет и возвращает первую задачу из очереди."""
        if not self._tasks:
            raise IndexError("Нельзя получить задачу из пустой очереди")
        return self._tasks.pop(0)

    def filter_by_status(self, status: str) -> Iterator[Task]:
        """Лениво возвращает задачи с указанным статусом."""
        for task in self:
            if task.status == status:
                yield task

    def filter_by_priority(self, priority: int) -> Iterator[Task]:
        """Лениво возвращает задачи с указанным приоритетом."""
        for task in self:
            if task.priority == priority:
                yield task

    def filter(
        self,
        *,
        status: str | None = None,
        priority: int | None = None,
    ) -> Iterator[Task]:
        """Лениво возвращает задачи, подходящие под все заданные условия."""
        for task in self:
            if status is not None and task.status != status:
                continue
            if priority is not None and task.priority != priority:
                continue
            yield task

    @staticmethod
    def _validate_task(task: Task) -> None:
        """Проверяет, что в очередь попадает именно объект `Task`."""
        if not isinstance(task, Task):
            raise TypeError("TaskQueue может хранить только объекты Task")
