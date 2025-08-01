from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Union

from app.schemas.annotations.ls_annotation import LSAnnotationCreate, LSAnnotationUpdate


class AnnotationRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


AnnotationCreateUnion = Annotated[
    Union[LSAnnotationCreate],
    Field(discriminator="annotation_type")
]


AnnotationUpdateUnion = Annotated[
    Union[LSAnnotationUpdate],
    Field(discriminator="annotation_type")
]