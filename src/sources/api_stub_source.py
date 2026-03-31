from typing import Iterable, TypedDict

from src.models.task import Task


class APIStubTask(TypedDict):
    """Структура словаря, имитирующего одну задачу из ответа внешнего API."""

    id: int
    description: str
    priority: int
    status: str


class APIStubSource:
    """Учебный источник задач с жёстко заданным набором данных.

    Используется как заглушка вместо реального сетевого API, чтобы
    можно было тестировать интеграцию и обработку задач без внешних
    зависимостей и нестабильных ответов.
    """

    def __init__(self) -> None:
        """Создаёт встроенный набор задач, похожий на результат API-запроса."""
        self.data: list[APIStubTask] = [
            {
                "id": 100,
                "description": "Обработать входящий webhook",
                "priority": 4,
                "status": "new",
            },
            {
                "id": 101,
                "description": "Пересчитать статистику по заказам",
                "priority": 2,
                "status": "in_progress",
            },
            {
                "id": 102,
                "description": "Отправить уведомление пользователю",
                "priority": 5,
                "status": "done",
            },
        ]

    def get_tasks(self) -> Iterable[Task]:
        """Преобразует внутренние словари заглушки в объекты доменной модели."""
        for item in self.data:
            yield Task(**item)
