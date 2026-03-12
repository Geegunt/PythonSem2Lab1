from typing import Iterable

from src.models.task import Task


class GeneratorSource:
    def __init__(self, count: int = 5):
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for i in range(self.count):
            yield Task(id=i, payload=f"generator_task_{i}")
