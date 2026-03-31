from typing import Iterable

from src.models.task import Task


class GeneratorSource:
    """Источник, генерирующий набор тестовых задач прямо в памяти.

    Удобен для демонстрации и тестов, когда не хочется зависеть от
    файловой системы или внешнего API, но нужен предсказуемый поток задач.
    """

    def __init__(self, count: int = 5) -> None:
        """Сохраняет количество задач, которое нужно сгенерировать при чтении."""
        self.count: int = count

    def get_tasks(self) -> Iterable[Task]:
        """Лениво создаёт указанное количество тестовых объектов `Task`."""
        for i in range(self.count):
            yield Task(
                id=i,
                description=f"Сгенерированная задача #{i + 1}",
                priority=(i % 5) + 1,
            )
