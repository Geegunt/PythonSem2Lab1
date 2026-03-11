from typing import List

from src.contracts.task_source import TaskSource
from src.models.task import Task


class TaskReceiver:
    def receive(self, source: TaskSource) -> List[Task]:
        return list(source.get_tasks())