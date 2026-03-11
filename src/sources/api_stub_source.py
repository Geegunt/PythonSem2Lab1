from typing import Iterable

from src.models.task import Task


class APIStubSource:
    def __init__(self):
        self.data = [
            {"id": 100, "payload": "api_task_1"},
            {"id": 101, "payload": "api_task_2"},
            {"id": 102, "payload": "api_task_3"},
        ]
    def get_tasks(self) -> Iterable[Tas
        k]:
        for item in self.data:
            yield Task(**item)