"""Project API routes.

This module contains all the endpoints for managing storages in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.storage import StorageCRUD
from app.db.database import get_session

from app.schemas.storage import StorageCreate, StorageRead, StorageUpdate


router = APIRouter(prefix="/storages", tags=["storages"])
storage_crud = StorageCRUD()


@router.post("/", response_model=StorageRead, status_code=status.HTTP_201_CREATED)
async def create_storage(
    storage: StorageCreate, session: AsyncSession = Depends(get_session)
) -> StorageRead:
    """Create a new storage."""

    return await storage_crud.create(storage, session)


@router.get("/", response_model=List[StorageRead])
async def get_storages(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
) -> List[StorageRead]:
    """Get all storages."""

    return await storage_crud.get_storages(skip, limit, session)


@router.get("/{project_id}", response_model=StorageRead)
async def get_project(
    storage_id: int, session: AsyncSession = Depends(get_session)
) -> StorageRead:
    """Get a storage by ID."""

    return await storage_crud.get_storage_by_id(storage_id, session)


@router.put("/{project_id}", response_model=StorageRead)
async def update_project(
    storage_id: int,
    storage_update: StorageUpdate,
    session: AsyncSession = Depends(get_session),
) -> StorageRead:
    """Update a storage."""

    return await storage_crud.update_storage(storage_id, storage_update, session)
