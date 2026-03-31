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
    """Доменная модель задачи с защищёнными атрибутами и вычисляемыми свойствами.

    Базовые поля `id`, `description`, `priority`, `status` и `created_at`
    управляются пользовательскими дескрипторами, поэтому проходят
    валидацию при каждом присваивании.

    Для обратной совместимости с первой лабораторной сохранён алиас
    `payload`, а свойство `short_description` демонстрирует работу
    non-data descriptor поверх основного описания задачи.
    """

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
        """Создаёт экземпляр задачи и инициализирует его в согласованном состоянии.

        Можно передать либо современное поле `description`, либо
        устаревший алиас `payload`. Если дата создания не указана,
        используется текущее время в UTC.
        """
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
        """Возвращает описание под старым именем поля для обратной совместимости.

        Свойство позволяет старому коду работать с новой моделью без
        дублирования состояния: фактически `payload` является алиасом
        к полю `description`.
        """
        return self.description

    @payload.setter
    def payload(self, value: str) -> None:
        """Обновляет описание задачи через устаревший алиас `payload`."""
        self.description = value

    @property
    def is_ready_for_execution(self) -> bool:
        """Возвращает `True`, если задача ещё не начата и готова к обработке."""
        return self.status == "new"

    @property
    def is_finished(self) -> bool:
        """Возвращает `True`, если задача завершена успешно или с ошибкой."""
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
