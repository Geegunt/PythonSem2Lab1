from src.contracts.task_source import TaskSource
from src.contracts.task_handler import ManagedTaskHandler, TaskHandler
from src.handlers.task_handlers import DefaultTaskHandler, PriorityTaskHandler
from src.sources.generator_source import GeneratorSource


def test_generator_source_implements_protocol():
    source = GeneratorSource()
    assert isinstance(source, TaskSource)


def test_priority_handler_implements_task_handler_protocol():
    handler = PriorityTaskHandler()
    assert isinstance(handler, TaskHandler)


def test_default_handler_implements_managed_task_handler_protocol():
    handler = DefaultTaskHandler()
    assert isinstance(handler, TaskHandler)
    assert isinstance(handler, ManagedTaskHandler)
