from __future__ import annotations
from datetime import datetime, UTC
from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from .project import Project


class AnnotationToolClient(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("url", "ls_project_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    url: str = Field(max_length=200)
    ls_project_id: int = Field()
    api_key: str = Field(max_length=1000) # unencrypted for now

    # project: Optional[Project] = Relationship(back_populates="annotation_tool_client")