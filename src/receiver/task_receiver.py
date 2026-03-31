from src.contracts.task_source import TaskSource
from src.models.task import Task


class TaskReceiver:
    """Сервисный объект для безопасного получения задач из источников.

    Класс проверяет, что переданный объект совместим с контрактом
    `TaskSource`, материализует результат в список и переводит ошибки
    источника в единый формат `RuntimeError` с понятным сообщением.
    """

    def receive(self, source: TaskSource) -> list[Task]:
        """Получает задачи из источника и возвращает их как готовый список.

        Такой слой удобен тем, что остальной код работает уже не с
        ленивым `Iterable`, а с предсказуемой коллекцией, при этом
        детали ошибок конкретного источника не протекают наружу.
        """
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
