from src.sources.api_stub_source import APIStubSource


def test_api_source_returns_tasks():
    source = APIStubSource()
    tasks = list(source.get_tasks())
    assert len(tasks) == 3


def test_api_source_task_structure():
    source = APIStubSource()
    task = next(source.get_tasks())
    assert hasattr(task, "id")
    assert hasattr(task, "payload")
