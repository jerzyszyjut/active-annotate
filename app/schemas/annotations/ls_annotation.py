from typing import Literal, Optional
from pydantic import BaseModel

from app.enums import AnnotationType


class LSAnnotationCreate(BaseModel):
    annotation_type: Literal[AnnotationType.label_studio]
    url: str
    ls_project_id: int
    api_key: str


class LSAnnotationUpdate(BaseModel):
    annotation_type: Literal[AnnotationType.label_studio]
    url: Optional[str]
    ls_project_id: Optional[int]
    api_key: Optional[str]


