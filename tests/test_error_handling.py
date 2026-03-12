import pytest
from src.sources.file_source import FileSource


def test_file_not_found():
    source = FileSource("data/does_not_exist.json")
    with pytest.raises(RuntimeError):
        list(source.get_tasks())
