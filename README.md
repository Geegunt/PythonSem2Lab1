# Лабораторная работа №4
## Асинхронный исполнитель задач

**Студент:** Григорьев Глеб Алексевич  
**Группа:** М8О-102БВ-25

---

## Описание работы

Проект является продолжением лабораторной работы №3 про очередь задач. Готовая
модель `Task`, источники задач, `TaskReceiver` и синхронная коллекция
`TaskQueue` сохранены. Новая часть добавляет асинхронный слой обработки:
`AsyncTaskQueue`, контракт обработчиков и `AsyncTaskExecutor`.

Основной акцент ЛР4 сделан на:

- корректном использовании `async / await`;
- асинхронной очереди задач на базе `asyncio.Queue`;
- расширяемом контракте обработчика через `typing.Protocol`;
- управлении ресурсами через async context manager;
- централизованном логировании и обработке ошибок;
- сохранении архитектурной связи с предыдущими лабораторными.

---

## Что переиспользовано из ЛР3

Из предыдущей работы сохранены:

- класс `Task` с дескрипторами, `property` и пользовательскими исключениями;
- источники задач `GeneratorSource`, `FileSource`, `APIStubSource`;
- контракт `TaskSource`;
- сервис `TaskReceiver`;
- пользовательская коллекция `TaskQueue` с итерацией и ленивыми фильтрами.

`AsyncTaskQueue.from_task_queue()` принимает обычную `TaskQueue` и переносит в
асинхронную очередь те же объекты `Task` без копирования.

---

## Асинхронная очередь `AsyncTaskQueue`

`AsyncTaskQueue` находится в `src/collections/async_task_queue.py`.

Она поддерживает:

- асинхронное добавление задач через `enqueue`;
- добавление без ожидания через `enqueue_nowait`;
- асинхронное получение задач через `dequeue`;
- получение без ожидания через `dequeue_nowait`;
- `task_done` и `join` для контроля завершения обработки;
- асинхронный обход через `async for`;
- создание из `TaskQueue` через `from_task_queue`.

Пример:

```python
from src.collections.async_task_queue import AsyncTaskQueue
from src.collections.task_queue import TaskQueue

sync_queue = TaskQueue(tasks)
async_queue = AsyncTaskQueue.from_task_queue(sync_queue)
task = await async_queue.dequeue()
async_queue.task_done()
```

---

## Контракт обработчика

Контракт описан в `src/contracts/task_handler.py`.

```python
@runtime_checkable
class TaskHandler(Protocol):
    def can_handle(self, task: Task) -> bool: ...
    async def handle(self, task: Task) -> None: ...
```

Для обработчиков, которым нужно открывать и закрывать ресурсы, добавлен
`ManagedTaskHandler` с методами `__aenter__` и `__aexit__`.

Обработчики не наследуются от общего базового класса. Исполнитель проверяет их
структурно через `isinstance(handler, TaskHandler)`, поэтому новые обработчики
можно добавлять без изменения существующего кода.

---

## Асинхронный исполнитель

`AsyncTaskExecutor` находится в `src/executor/async_task_executor.py`.

Он:

- запускается через `async with`;
- открывает ресурсы обработчиков, реализующих `ManagedTaskHandler`;
- забирает задачи из `AsyncTaskQueue`;
- выбирает первый обработчик, у которого `can_handle(task)` возвращает `True`;
- переводит статус задачи в `in_progress`, `done` или `failed`;
- логирует старт, успешное завершение и ошибки;
- возвращает список `TaskExecutionResult`;
- может работать с несколькими воркерами через `max_workers`.

Пример:

```python
from src.executor.async_task_executor import AsyncTaskExecutor
from src.handlers.task_handlers import DefaultTaskHandler, PriorityTaskHandler

handlers = [
    PriorityTaskHandler(min_priority=5),
    DefaultTaskHandler(),
]

async with AsyncTaskExecutor(handlers, max_workers=2) as executor:
    results = await executor.run(async_queue)
```

---

## Структура проекта

```text
src/
├── collections/
│   ├── async_task_queue.py
│   └── task_queue.py
├── contracts/
│   ├── task_handler.py
│   └── task_source.py
├── executor/
│   └── async_task_executor.py
├── handlers/
│   └── task_handlers.py
├── models/
│   ├── descriptors.py
│   ├── exceptions.py
│   └── task.py
├── receiver/
│   └── task_receiver.py
└── sources/
    ├── api_stub_source.py
    ├── file_source.py
    └── generator_source.py
```

---

## Тестирование

Для ЛР4 добавлены тесты:

- `tests/test_async_task_queue.py`;
- `tests/test_async_task_executor.py`;
- дополнительные проверки в `tests/test_protocol.py`.

Проверяется:

- FIFO-порядок асинхронной очереди;
- создание `AsyncTaskQueue` из `TaskQueue` без копирования задач;
- поддержка `async for`;
- запрет на добавление объектов не типа `Task`;
- runtime-проверка `TaskHandler` и `ManagedTaskHandler`;
- управление ресурсами обработчиков через `async with`;
- выбор первого подходящего обработчика;
- централизованное логирование ошибки;
- перевод задачи в статус `failed` при исключении обработчика.

Запуск тестов:

```bash
pytest
```

---

## Соответствие требованиям ЛР4

В работе реализованы требования лабораторной:

- асинхронная очередь задач реализована через `asyncio.Queue`;
- контракт обработчика описан через `Protocol` и `runtime_checkable`;
- исполнитель использует `async with` и async context managers обработчиков;
- обработка задач выполняется через `async / await`;
- демонстрационные обработчики используют `asyncio.sleep`, а не блокирующие
  задержки;
- ошибки обработчиков централизованно логируются в `AsyncTaskExecutor`;
- архитектура позволяет добавлять новые обработчики без изменения очереди и
  исполнителя;
- все публичные интерфейсы снабжены аннотациями типов и документацией.
