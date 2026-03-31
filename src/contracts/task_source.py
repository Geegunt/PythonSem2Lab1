from typing import Protocol, Iterable, runtime_checkable

from src.models.task import Task


@runtime_checkable
class TaskSource(Protocol):
    """Контракт для любого источника, способного поставлять задачи.

    Источник должен предоставлять метод `get_tasks`, возвращающий
    итерируемую последовательность объектов `Task`. Использование
    `Protocol` позволяет проверять совместимость по структуре, а не
    по явному наследованию.
    """

    def get_tasks(self) -> Iterable[Task]:
        """Возвращает задачи из произвольного источника в виде `Iterable[Task]`."""
        ...
