from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func


class ProjectBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    active_learning_batch_size: int = Field(default=10, ge=1, le=1000)
    description: Optional[str] = Field(default=None, max_length=1000)


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    active_learning_batch_size: Optional[int] = Field(default=None, ge=1, le=1000)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
