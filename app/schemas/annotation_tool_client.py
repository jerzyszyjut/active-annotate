from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AnnotationToolClientCreate(BaseModel):
    ip_address: str
    port: int
    ls_project_id: Optional[int] = None
    api_key: str


class AnnotationToolClientUpdate(BaseModel):
    ip_address: Optional[str] = None
    port: Optional[int] = None
    ls_project_id: Optional[int] = None
    api_key: Optional[str] = None


class AnnotationToolClientRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    ip_address: str
    port: int
    ls_project_id: int
    api_key: str

    model_config = {
        "from_attributes": True
    }