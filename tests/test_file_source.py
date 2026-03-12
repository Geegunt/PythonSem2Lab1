from src.sources.file_source import FileSource


def test_file_source_reads_tasks():
    source = FileSource("data/tasks.json")
    tasks = list(source.get_tasks())
    assert len(tasks) > 0


def test_file_source_task_structure():
    source = FileSource("data/tasks.json")
    task = next(source.get_tasks())
    assert hasattr(task, "id")
    assert hasattr(task, "payload")
