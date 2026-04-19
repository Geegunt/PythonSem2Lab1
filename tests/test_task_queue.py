from collections.abc import Iterator

import pytest

from src.collections.task_queue import TaskQueue
from src.models.task import Task


def make_tasks() -> list[Task]:
    return [
        Task(id=1, description="Принять заявку", priority=5, status="new"),
        Task(id=2, description="Проверить оплату", priority=3, status="in_progress"),
        Task(id=3, description="Отправить письмо", priority=5, status="done"),
        Task(id=4, description="Обновить отчёт", priority=1, status="done"),
    ]


def test_task_queue_supports_for_loop_iteration():
    queue = TaskQueue(make_tasks())
    ids: list[int] = []

    for task in queue:
        ids.append(task.id)

    assert ids == [1, 2, 3, 4]


def test_task_queue_supports_repeated_iteration():
    queue = TaskQueue(make_tasks())

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == [1, 2, 3, 4]
    assert second_pass == [1, 2, 3, 4]


def test_task_queue_is_compatible_with_list_and_sum():
    queue = TaskQueue(make_tasks())

    tasks_as_list = list(queue)
    total_priority = sum(task.priority for task in queue)

    assert len(tasks_as_list) == 4
    assert total_priority == 14


def test_filter_by_status_is_lazy_generator():
    queue = TaskQueue(make_tasks())

    done_tasks = queue.filter_by_status("done")
    queue.enqueue(Task(id=5, description="Закрыть смену", priority=2, status="done"))

    assert isinstance(done_tasks, Iterator)
    assert [task.id for task in done_tasks] == [3, 4, 5]


def test_filter_by_priority_is_lazy_generator():
    queue = TaskQueue(make_tasks())

    high_priority_tasks = queue.filter_by_priority(5)
    queue.enqueue(Task(id=5, description="Срочно позвонить", priority=5))

    assert isinstance(high_priority_tasks, Iterator)
    assert [task.id for task in high_priority_tasks] == [1, 3, 5]


def test_combined_filter_uses_status_and_priority():
    queue = TaskQueue(make_tasks())

    result = queue.filter(status="done", priority=5)

    assert [task.id for task in result] == [3]


def test_queue_stores_existing_task_objects_without_copying_them():
    task = Task(id=10, description="Исходная задача", priority=2, status="new")
    queue = TaskQueue([task])

    task.status = "done"

    assert list(queue.filter_by_status("done")) == [task]


def test_enqueue_accepts_only_task_instances():
    queue = TaskQueue()

    with pytest.raises(TypeError):
        queue.enqueue("not a task")


def test_dequeue_returns_tasks_in_fifo_order():
    queue = TaskQueue(make_tasks())

    first_task = queue.dequeue()

    assert first_task.id == 1
    assert [task.id for task in queue] == [2, 3, 4]
