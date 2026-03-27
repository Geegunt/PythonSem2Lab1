from datetime import datetime, timezone

import pytest

from src.models.exceptions import (
    TaskCreatedAtValidationError,
    TaskDescriptionValidationError,
    TaskIdValidationError,
    TaskPriorityValidationError,
    TaskStatusValidationError,
)
from src.models.task import Task


def test_task_exposes_safe_public_api():
    created_at = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    task = Task(
        id=10,
        description="Обработать заказ #10",
        priority=4,
        status="in_progress",
        created_at=created_at,
    )

    assert task.id == 10
    assert task.description == "Обработать заказ #10"
    assert task.priority == 4
    assert task.status == "in_progress"
    assert task.created_at == created_at
    assert task.payload == "Обработать заказ #10"
    assert task.short_description == "Обработать заказ #10"
    assert not task.is_ready_for_execution
    assert not task.is_finished


def test_task_accepts_legacy_payload_alias():
    task = Task(id=7, payload="Старый формат задачи")

    assert task.description == "Старый формат задачи"
    assert task.payload == "Старый формат задачи"
    assert task.priority == 3
    assert task.status == "new"
    assert task.is_ready_for_execution


def test_payload_property_updates_description():
    task = Task(id=5, description="Исходное описание")

    task.payload = "Обновлённое описание"

    assert task.description == "Обновлённое описание"
    assert task.payload == "Обновлённое описание"


def test_finished_property_for_done_status():
    task = Task(id=6, description="Завершённая задача", status="done")

    assert task.is_finished
    assert not task.is_ready_for_execution


def test_data_descriptor_has_priority_over_instance_dictionary():
    task = Task(id=11, description="Настоящее описание")
    task.__dict__["description"] = "Подменённое описание"

    assert task.description == "Настоящее описание"


def test_non_data_descriptor_can_be_shadowed():
    task = Task(id=12, description="Очень длинное описание задачи для превью")
    computed_preview = task.short_description

    task.short_description = "Ручное превью"

    assert computed_preview == "Очень длинное описани..."
    assert task.short_description == "Ручное превью"


@pytest.mark.parametrize(
    ("kwargs", "error_type"),
    [
        ({"id": -1, "description": "ok"}, TaskIdValidationError),
        ({"id": 1, "description": "   "}, TaskDescriptionValidationError),
        ({"id": 1, "description": "ok", "priority": 10}, TaskPriorityValidationError),
        ({"id": 1, "description": "ok", "status": "queued"}, TaskStatusValidationError),
        (
            {"id": 1, "description": "ok", "created_at": "2026-03-27"},
            TaskCreatedAtValidationError,
        ),
    ],
)
def test_task_validation_errors(kwargs, error_type):
    with pytest.raises(error_type):
        Task(**kwargs)
