from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AnnotationToolClientCreate(BaseModel):
    url: str
    ls_project_id: int
    api_key: str


class AnnotationToolClientUpdate(BaseModel):
    url: Optional[str]
    ls_project_id: Optional[int]
    api_key: Optional[str]


class AnnotationToolClientRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    url: str
    ls_project_id: int
    api_key: str

    model_config = {
        "from_attributes": True
    }