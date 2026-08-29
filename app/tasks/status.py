from enum import Enum


class TaskStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
