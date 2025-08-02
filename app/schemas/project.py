from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    active_learning_batch_size: int
    description: Optional[str]
    annotation_tool_client_id: Optional[int]
    storage_id: Optional[int]

class ProjectUpdate(BaseModel):
    name: Optional[str]
    active_learning_batch_size: Optional[int]
    description: Optional[str]
    annotation_tool_client_id: Optional[int]
    storage_id: Optional[int]

class ProjectRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    name: str
    active_learning_batch_size: int
    description: Optional[str]
    annotation_tool_client_id: Optional[int]
    storage_id: Optional[int]

    model_config = {
        "from_attributes": True
    }