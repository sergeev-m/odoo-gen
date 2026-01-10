from enum import Enum, auto


class WriteMode(Enum):
    CREATE = "create"
    OVERWRITE = "overwrite"
    MODIFY = "modify"
    APPEND = "append"
    SKIP = "skip"


class StepAction(Enum):
    MKDIR = "mkdir"
    WRITE = "write"
    DELETE = "delete"


class MenuState(Enum):
    SKIP = auto()
    NEED = auto()
    READY = auto()
