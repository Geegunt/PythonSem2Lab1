import json
from typing import Iterable

from src.models.task import Task


class FileSource:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_tasks(self) -> Iterable[Task]:
        try:
            with open(self.filepath, encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise RuntimeError(f"Файл с задачами не найден: {self.filepath}")

        except json.JSONDecodeError:
            raise RuntimeError(f"Ошибка чтения JSON в файле: {self.filepath}")

        for item in data:
            if not isinstance(item, dict):
                raise RuntimeError("Неверный формат задачи в JSON")
            if "id" not in item or "payload" not in item:
                raise RuntimeError("Задача должна содержать поля id и payload")

            yield Task(**item)
