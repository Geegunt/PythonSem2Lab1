from __future__ import annotations

from datetime import datetime, timezone

from src.models.descriptors import (
    TaskCreatedAtDescriptor,
    TaskDescriptionDescriptor,
    TaskIdDescriptor,
    TaskPreviewDescriptor,
    TaskPriorityDescriptor,
    TaskStatusDescriptor,
)
from src.models.exceptions import TaskDescriptionValidationError


class Task:
    id = TaskIdDescriptor()
    description = TaskDescriptionDescriptor()
    priority = TaskPriorityDescriptor()
    status = TaskStatusDescriptor()
    created_at = TaskCreatedAtDescriptor()
    short_description = TaskPreviewDescriptor()

    def __init__(
        self,
        id: int,
        description: str | None = None,
        *,
        payload: str | None = None,
        priority: int = 3,
        status: str = "new",
        created_at: datetime | None = None,
    ) -> None:
        """Создаёт задачу и проверяет корректность переданных данных."""
        resolved_description = description if description is not None else payload
        if resolved_description is None:
            raise TaskDescriptionValidationError(
                "Нужно передать description или payload для создания задачи"
            )

        self.id = id
        self.description = resolved_description
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)

    @property
    def payload(self) -> str:
        """Возвращает описание задачи под именем из старой версии модели."""
        return self.description

    @payload.setter
    def payload(self, value: str) -> None:
        self.description = value

    @property
    def is_ready_for_execution(self) -> bool:
        """Показывает, готова ли задача к запуску в обработку."""
        return self.status == "new"

    @property
    def is_finished(self) -> bool:
        """Показывает, завершена ли задача успешно или с ошибкой."""
        return self.status in {"done", "failed"}

    def __repr__(self) -> str:
        return (
            "Task("
            f"id={self.id}, "
            f"description={self.description!r}, "
            f"priority={self.priority}, "
            f"status={self.status!r}, "
            f"created_at={self.created_at.isoformat()!r}"
            ")"
        )

    def __str__(self) -> str:
        return f"Task #{self.id}: {self.description}"
