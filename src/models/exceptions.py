class TaskValidationError(ValueError):
    pass


class TaskIdValidationError(TaskValidationError):
    pass


class TaskDescriptionValidationError(TaskValidationError):
    pass


class TaskPriorityValidationError(TaskValidationError):
    pass


class TaskStatusValidationError(TaskValidationError):
    pass


class TaskCreatedAtValidationError(TaskValidationError):
    pass
