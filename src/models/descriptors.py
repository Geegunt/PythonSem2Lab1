from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models.exceptions import (
    TaskCreatedAtValidationError,
    TaskDescriptionValidationError,
    TaskIdValidationError,
    TaskPriorityValidationError,
    TaskStatusValidationError,
)

ALLOWED_TASK_STATUSES = frozenset({"new", "in_progress", "done", "failed"})


class BaseTaskDescriptor:
    """Базовый data descriptor для атрибутов модели `Task`.

    Класс инкапсулирует общую механику работы дескриптора:
    привязку к имени атрибута, чтение значения из `__dict__` экземпляра
    и запись только после валидации.

    Наследники переопределяют метод `validate`, чтобы задать правила
    проверки и нормализации конкретного поля задачи.
    """

    def __set_name__(self, owner: type[object], name: str) -> None:
        """Запоминает публичное и внутреннее имя атрибута при создании класса."""
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[object]) -> Any:
        """Возвращает дескриптор у класса и сохранённое значение у экземпляра."""
        if instance is None:
            return self
        return instance.__dict__[self.storage_name]

    def __set__(self, instance: object, value: Any) -> None:
        """Сохраняет значение в экземпляре только после успешной валидации."""
        instance.__dict__[self.storage_name] = self.validate(value)

    def validate(self, value: Any) -> Any:
        """Возвращает значение без изменений.

        Метод предназначен для переопределения в дочерних дескрипторах,
        где выполняется фактическая проверка типа, диапазона и формата.
        """
        return value


class TaskIdDescriptor(BaseTaskDescriptor):
    """Проверяет корректность идентификатора задачи.

    Допускаются только неотрицательные целые числа.
    Булевы значения отклоняются отдельно, хотя в Python они являются
    подклассом `int`, потому что для идентификатора это было бы
    неочевидным и нежелательным поведением.
    """

    def validate(self, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TaskIdValidationError("Идентификатор задачи должен быть целым числом")
        if value < 0:
            raise TaskIdValidationError(
                "Идентификатор задачи не может быть отрицательным"
            )
        return value


class TaskDescriptionDescriptor(BaseTaskDescriptor):
    """Проверяет и нормализует текстовое описание задачи.

    Дескриптор принимает только строки, удаляет пробелы по краям и
    запрещает пустое описание после очистки. Благодаря этому модель
    хранит описание в предсказуемом и готовом к отображению виде.
    """

    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TaskDescriptionValidationError("Описание задачи должно быть строкой")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise TaskDescriptionValidationError("Описание задачи не может быть пустым")

        return cleaned_value


class TaskPriorityDescriptor(BaseTaskDescriptor):
    """Ограничивает приоритет задачи целочисленным диапазоном от 1 до 5."""

    def validate(self, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TaskPriorityValidationError(
                "Приоритет задачи должен быть целым числом"
            )
        if not 1 <= value <= 5:
            raise TaskPriorityValidationError(
                "Приоритет задачи должен быть в диапазоне от 1 до 5"
            )
        return value


class TaskStatusDescriptor(BaseTaskDescriptor):
    """Проверяет статус задачи по фиксированному набору допустимых значений.

    Строка предварительно очищается от внешних пробелов, после чего
    сравнивается с перечнем поддерживаемых статусов, определённым
    в `ALLOWED_TASK_STATUSES`.
    """

    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TaskStatusValidationError("Статус задачи должен быть строкой")

        cleaned_value = value.strip()
        if cleaned_value not in ALLOWED_TASK_STATUSES:
            allowed_values = ", ".join(sorted(ALLOWED_TASK_STATUSES))
            raise TaskStatusValidationError(
                f"Статус задачи должен быть одним из: {allowed_values}"
            )

        return cleaned_value


class TaskCreatedAtDescriptor(BaseTaskDescriptor):
    """Разрешает хранить дату создания только как объект `datetime`."""

    def validate(self, value: Any) -> datetime:
        if not isinstance(value, datetime):
            raise TaskCreatedAtValidationError(
                "Время создания задачи должно быть экземпляром datetime"
            )
        return value


class TaskPreviewDescriptor:
    """Вычисляет короткое превью описания задачи.

    Это non-data descriptor: он реализует только `__get__`, поэтому
    может быть затенён одноимённым атрибутом экземпляра. Такое
    поведение специально сохранено в учебных целях, чтобы показать
    отличие от data descriptor, использованных для основных полей `Task`.
    """

    def __get__(
        self, instance: Any | None, owner: type[object]
    ) -> str | TaskPreviewDescriptor:
        """Возвращает сокращённое описание длиной до 24 символов."""
        if instance is None:
            return self

        description = instance.description
        if len(description) <= 24:
            return description
        return f"{description[:21]}..."
