from src.receiver.task_receiver import TaskReceiver
from src.sources.generator_source import GeneratorSource


def test_receiver_collects_tasks():
    receiver = TaskReceiver()
    source = GeneratorSource(4)
    tasks = receiver.receive(source)
    assert len(tasks) == 4


def test_receiver_returns_list():
    receiver = TaskReceiver()
    source = GeneratorSource(2)
    tasks = receiver.receive(source)
    assert isinstance(tasks, list)
