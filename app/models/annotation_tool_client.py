from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint
from sqlalchemy import Column, DateTime, func


class AnnotationToolClient(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("ip_address", "ls_project_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    ip_address: str = Field(max_length=200)
    port: int = Field()
    ls_project_id: Optional[int] = Field(default=None)
    api_key: str = Field(max_length=1000)  # unencrypted for now
