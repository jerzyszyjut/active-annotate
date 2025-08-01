from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func
from sqlalchemy.types import Enum as SQLEnum

from app.enums import AnnotationType


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    annotation_type: AnnotationType = Field(sa_column=Column(SQLEnum(AnnotationType)))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )