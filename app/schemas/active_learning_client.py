from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ActiveLearningClientCreate(BaseModel):
    data: dict


class ActiveLearningClientUpdate(BaseModel):
    data: Optional[dict]


class ActiveLearningClientRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    data: dict

    model_config = {"from_attributes": True}
