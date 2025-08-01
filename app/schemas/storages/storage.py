from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Union

from app.schemas.storages.local_storage import LocalStorageCreate, LocalStorageUpdate


class StorageRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


StorageCreateUnion = Annotated[
    Union[LocalStorageCreate],
    Field(discriminator="storage_type")
]


StorageUpdateUnion = Annotated[
    Union[LocalStorageUpdate],
    Field(discriminator="storage_type")
]