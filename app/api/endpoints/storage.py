"""Project API routes.

This module contains all the endpoints for managing storages in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.crud.storage import StorageCRUD
from app.db.database import get_session
from app.models.storage import Storage

from app.schemas.storage import (
    StorageCreate,
    StorageRead,
    StorageUpdate
)


router = APIRouter(prefix="/storages", tags=["storages"])
storage_crud = StorageCRUD()

@router.post("/", response_model=StorageRead, status_code=status.HTTP_201_CREATED)
async def create_storage(
    storage: StorageCreate,
    session: AsyncSession = Depends(get_session)
) -> StorageRead:
    """Create a new storage."""

    return await storage_crud.create(storage, session)