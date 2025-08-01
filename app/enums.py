from enum import Enum


class AnnotationType(str, Enum):
    label_studio = "label-studio"

class StorageType(str, Enum):
    local_storage = "local-storage"