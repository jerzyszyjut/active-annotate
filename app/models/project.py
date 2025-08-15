from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    name: str = Field(index=True, min_length=1, max_length=200)
    active_learning_batch_size: int = Field(default=10, ge=1, le=1000)
    label_config: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=1000)
    epoch: int = Field(default=0)
    ml_backend_url: Optional[str] = Field(default=None, max_length=1000)

    annotation_tool_client_id: Optional[int] = Field(
        default=None, foreign_key="annotationtoolclient.id"
    )
    storage_id: Optional[int] = Field(
        default=None, foreign_key="storage.id"
    )
    active_learning_client_id: Optional[int] = Field(
        default=None, foreign_key="activelearningclient.id"
    )