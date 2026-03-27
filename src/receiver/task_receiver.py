from src.contracts.task_source import TaskSource
from src.models.task import Task


class TaskReceiver:
    def receive(self, source: TaskSource) -> list[Task]:
        if not isinstance(source, TaskSource):
            raise TypeError(f"{type(source).__name__} не реализует контракт TaskSource")
        try:
            tasks = list(source.get_tasks())
        except Exception as error:
            raise RuntimeError(
                f"Произошла ошибка при получении задач из источника "
                f"{type(source).__name__}"
            ) from error
        return tasks
