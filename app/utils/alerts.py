from enum import Enum

class Type(Enum):
    OK = "ok"
    ACTION = "action"
    ERROR = "error"
    WARNING = "warning"
    
class Status(Enum):
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"