import json
from typing import Iterable

from src.models.task import Task


class FileSource:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_tasks(self) -> Iterable[Task]:
        with open(self.filepath, encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            yield Task(**item)