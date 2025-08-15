from __future__ import annotations
from datetime import datetime, UTC
from typing import Any, Optional
from sqlmodel import SQLModel, Field 
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB


class ActiveLearningClient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    data: Any = Field(sa_column=Column(JSONB))