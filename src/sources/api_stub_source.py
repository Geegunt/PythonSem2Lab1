from typing import Iterable, TypedDict

from src.models.task import Task


class APIStubTask(TypedDict):
    id: int
    description: str
    priority: int
    status: str


class APIStubSource:
    def __init__(self) -> None:
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
        for item in self.data:
            yield Task(**item)
