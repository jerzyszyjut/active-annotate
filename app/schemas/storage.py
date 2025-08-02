from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class StorageCreate(BaseModel):
    path: str


class StorageUpdate(BaseModel):
    path: Optional[str]


class StorageRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    path: str

    model_config = {
        "from_attributes": True
    }
