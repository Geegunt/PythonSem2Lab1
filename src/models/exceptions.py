class TaskValidationError(ValueError):
    """Базовое исключение для всех ошибок валидации модели `Task`."""

    pass


class TaskIdValidationError(TaskValidationError):
    """Выбрасывается при некорректном значении идентификатора задачи."""

    pass


class TaskDescriptionValidationError(TaskValidationError):
    """Выбрасывается, когда описание задачи отсутствует или имеет неверный формат."""

    pass


class TaskPriorityValidationError(TaskValidationError):
    """Выбрасывается при передаче приоритета вне допустимого диапазона."""

    pass


class TaskStatusValidationError(TaskValidationError):
    """Выбрасывается, если статус задачи не входит в список допустимых."""

    pass


class TaskCreatedAtValidationError(TaskValidationError):
    """Выбрасывается, когда дата создания передана не как `datetime`."""

    pass
