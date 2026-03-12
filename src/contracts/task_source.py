from typing import Protocol, Iterable, runtime_checkable

from src.models.task import Task


@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterable[Task]: ...
