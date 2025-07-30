from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

from models.project import Project


class LocalStorageBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    path: str = Field(min_length=1, max_length=1000)

class LocalStorage(LocalStorageBase, table=True):
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

class LocalStorageCreate(LocalStorageBase):
    pass

class LocalStorageUpdate(SQLModel):
    name: Optional[str] = Field(index=True, min_length=1, max_length=200)
    path: Optional[str] = Field(min_length=1, max_length=1000)

class LocalStorageRead(SQLModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

