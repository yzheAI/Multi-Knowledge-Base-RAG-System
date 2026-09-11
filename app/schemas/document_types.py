from enum import Enum


class DocumentType(str, Enum):
    EQUIPMENT = 'equipment'
    OPERATION = 'operation'
    DIAGNOSIS = 'diagnosis'
    COMMISSIONING = 'commissioning'
    PROGRAMMING = 'programming'
    PARAMETER = 'parameter'
    FUNCTION = 'function'
    SAFETY = 'safety'
    INSTALLATION = 'installation'


class ChunkStatus(str, Enum):
    PENDING = 'pending'
    INDEXED = 'indexed'
    FAILED = 'failed'
