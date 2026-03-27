from src.contracts.task_source import TaskSource
from src.receiver.task_receiver import TaskReceiver

from src.sources.generator_source import GeneratorSource
from src.sources.file_source import FileSource
from src.sources.api_stub_source import APIStubSource


def main() -> None:
    """Запускает демонстрационную обработку задач из всех доступных источников."""
    receiver = TaskReceiver()
    sources: list[TaskSource] = [
        GeneratorSource(3),
        FileSource("data/tasks.json"),
        APIStubSource(),
    ]
    for source in sources:
        print(f"\nSource: {source.__class__.__name__}")
        tasks = receiver.receive(source)
        for task in tasks:
            print(task)


if __name__ == "__main__":
    main()
