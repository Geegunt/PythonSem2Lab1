from src.sources.generator_source import GeneratorSource


def test_generator_source_returns_tasks():
    source = GeneratorSource(1)
    task = next(source.get_tasks())
    assert task.id == 0
    assert task.payload is not None


def test_generator_source_id_sequence():
    source = GeneratorSource(3)
    tasks = list(source.get_tasks())
    assert tasks[0].id == 0
    assert tasks[1].id == 1
    assert tasks[2].id == 2
