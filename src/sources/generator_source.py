from typing import Iterable

from src.models.task import Task


class GeneratorSource:
    def __init__(self, count: int = 5) -> None:
        """Настраивает количество задач, которое будет сгенерировано."""
        self.count: int = count

    def get_tasks(self) -> Iterable[Task]:
        """Генерирует тестовые задачи в памяти."""
        for i in range(self.count):
            yield Task(
                id=i,
                description=f"Сгенерированная задача #{i + 1}",
                priority=(i % 5) + 1,
            )
