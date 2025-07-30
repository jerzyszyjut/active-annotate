from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

from models.project import Project


class LSAnnotationBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    url: str = Field(default=None, max_length=200)
    ls_project_id: int = Field(default=None, unique=True)
    api_key: str = Field(default=None) # unencrypted for now

class LSAnnotation(LSAnnotationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    project_id: int | None = Field(default=None, foreign_key="project.id")
    project: Project | None = Relationship(back_populates="project")


class LSAnnotationCreate(LSAnnotationBase):
    pass


class LSAnnotationUpdate(SQLModel):
    name: Optional[int] = Field(index=True, min_length=1, max_length=200)
    url: Optional[str] = Field(default=None, max_length=200)
    ls_project_id: Optional[int] = Field(default=None, unique=True)
    api_key: Optional[str] = Field(default=None) # unencrypted for now


class LSAnnotationRead(SQLModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

