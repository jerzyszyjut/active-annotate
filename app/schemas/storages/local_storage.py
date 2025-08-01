from typing import Literal, Optional
from pydantic import BaseModel

from app.enums import StorageType


class LocalStorageCreate(BaseModel):
    storage_type: Literal[StorageType.local_storage]
    path: str


class LocalStorageUpdate(BaseModel):
    storage_type: Literal[StorageType.local_storage]
    path: Optional[str]


