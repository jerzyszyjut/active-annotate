"""Project API routes.

This module contains all the endpoints for managing active learning clients in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.active_learning_client import ActiveLearningClientCRUD
from app.db.database import get_session

from app.schemas.active_learning_client import (
    ActiveLearningClientCreate,
    ActiveLearningClientRead,
    ActiveLearningClientUpdate,
)


router = APIRouter(prefix="/active-learning-client", tags=["active_learning_client"])
active_learning_client_crud = ActiveLearningClientCRUD()


@router.post(
    "/", response_model=ActiveLearningClientRead, status_code=status.HTTP_201_CREATED
)
async def create_active_learning_client(
    active_learning_client: ActiveLearningClientCreate,
    session: AsyncSession = Depends(get_session),
) -> ActiveLearningClientRead:
    """Create a new active learning client."""

    return await active_learning_client_crud.create_active_learning_client(
        active_learning_client, session
    )


@router.get("/", response_model=List[ActiveLearningClientRead])
async def get_active_learning_clients(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
) -> List[ActiveLearningClientRead]:
    """Get all active learning clients."""

    return await active_learning_client_crud.get_active_learning_clients(
        skip, limit, session
    )


@router.get("/{active_learning_client_id}", response_model=ActiveLearningClientRead)
async def get_active_learning_client(
    active_learning_client_id: int, session: AsyncSession = Depends(get_session)
) -> ActiveLearningClientRead:
    """Get an active learning client by ID."""

    return await active_learning_client_crud.get_active_learning_client_by_id(
        active_learning_client_id, session
    )


@router.put("/{active_learning_client_id}", response_model=ActiveLearningClientRead)
async def update_active_learning_client(
    active_learning_client_id: int,
    active_learning_client_update: ActiveLearningClientUpdate,
    session: AsyncSession = Depends(get_session),
) -> ActiveLearningClientRead:
    """Update an active learning client."""

    return await active_learning_client_crud.update_active_learning_client(
        active_learning_client_id, active_learning_client_update, session
    )
