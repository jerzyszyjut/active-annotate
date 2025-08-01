from app.models.annotations.ls_annotation import LSAnnotation
from app.models.storages.local_storage import LocalStorage


ANNOTATION_MAP = {
    "label-studio": LSAnnotation
}

STORAGE_MAP = {
    "local-storage": LocalStorage
}