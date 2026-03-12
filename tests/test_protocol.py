from src.contracts.task_source import TaskSource
from src.sources.generator_source import GeneratorSource


def test_generator_source_implements_protocol():
    source = GeneratorSource()
    assert isinstance(source, TaskSource)
