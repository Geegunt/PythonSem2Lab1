import json
from typing import Iterable

from src.models.exceptions import TaskValidationError
from src.models.task import Task


class FileSource:
    """Источник задач, считывающий данные из JSON-файла.

    Каждый элемент массива в файле интерпретируется как набор аргументов
    для создания объекта `Task`. Ошибки структуры JSON и ошибки
    валидации модели преобразуются в понятные сообщения уровня источника.
    """

    def __init__(self, filepath: str) -> None:
        """Запоминает путь к файлу, из которого затем будут загружаться задачи."""
        self.filepath: str = filepath

    def get_tasks(self) -> Iterable[Task]:
        """Поэлементно преобразует JSON-данные в последовательность объектов `Task`.

        Метод является генератором: объекты задач отдаются по мере
        обработки элементов массива. При некорректной структуре данных
        выбрасывается `RuntimeError` с причиной проблемы.
        """
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
            if "id" not in item:
                raise RuntimeError("Задача должна содержать поле id")
            if "description" not in item and "payload" not in item:
                raise RuntimeError(
                    "Задача должна содержать поле description или payload"
                )

            try:
                yield Task(**item)
            except TaskValidationError as error:
                raise RuntimeError(f"Некорректные данные задачи: {error}") from error
            except TypeError as error:
                raise RuntimeError(
                    "JSON содержит неподдерживаемые поля задачи"
                ) from error
