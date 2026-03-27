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
    def __set_name__(self, owner: type[object], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[object]) -> Any:
        if instance is None:
            return self
        return instance.__dict__[self.storage_name]

    def __set__(self, instance: object, value: Any) -> None:
        instance.__dict__[self.storage_name] = self.validate(value)

    def validate(self, value: Any) -> Any:
        return value


class TaskIdDescriptor(BaseTaskDescriptor):
    def validate(self, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TaskIdValidationError("Идентификатор задачи должен быть целым числом")
        if value < 0:
            raise TaskIdValidationError(
                "Идентификатор задачи не может быть отрицательным"
            )
        return value


class TaskDescriptionDescriptor(BaseTaskDescriptor):
    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TaskDescriptionValidationError("Описание задачи должно быть строкой")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise TaskDescriptionValidationError("Описание задачи не может быть пустым")

        return cleaned_value


class TaskPriorityDescriptor(BaseTaskDescriptor):
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
    def validate(self, value: Any) -> datetime:
        if not isinstance(value, datetime):
            raise TaskCreatedAtValidationError(
                "Время создания задачи должно быть экземпляром datetime"
            )
        return value


class TaskPreviewDescriptor:
    def __get__(
        self, instance: Any | None, owner: type[object]
    ) -> str | TaskPreviewDescriptor:
        if instance is None:
            return self

        description = instance.description
        if len(description) <= 24:
            return description
        return f"{description[:21]}..."
