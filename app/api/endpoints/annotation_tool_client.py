"""Project API routes.

This module contains all the endpoints for managing annotation tools in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.db.database import get_session

from app.schemas.annotation_tool_client import (
    AnnotationToolClientCreate,
    AnnotationToolClientRead,
    AnnotationToolClientUpdate,
)


router = APIRouter(prefix="/annotation-tool-client", tags=["annotation_tool_client"])
annotation_tool_client_crud = AnnotationToolClientCRUD()


@router.post(
    "/", response_model=AnnotationToolClientRead, status_code=status.HTTP_201_CREATED
)
async def create_annotation_tool_client(
    annotation_tool_client: AnnotationToolClientCreate,
    session: AsyncSession = Depends(get_session),
) -> AnnotationToolClientRead:
    """Create an new annotation tool client."""

    return await annotation_tool_client_crud.create_annotation_tool(
        annotation_tool_client, session
    )


@router.get("/", response_model=List[AnnotationToolClientRead])
async def get_annotation_tool_clients(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
) -> List[AnnotationToolClientRead]:
    """Get all annotation tool clients."""

    return await annotation_tool_client_crud.get_annotation_tool_clients(
        skip, limit, session
    )


@router.get("/{project_id}", response_model=AnnotationToolClientRead)
async def get_annotation_tool_client(
    annotation_tool_client_id: int, session: AsyncSession = Depends(get_session)
) -> AnnotationToolClientRead:
    """Get an annotation tool client by ID."""

    return await annotation_tool_client_crud.get_annotation_tool_client_by_id(
        annotation_tool_client_id, session
    )


@router.put("/{project_id}", response_model=AnnotationToolClientRead)
async def update_annotation_tool_client(
    annotation_tool_client_id: int,
    annotation_tool_client_update: AnnotationToolClientUpdate,
    session: AsyncSession = Depends(get_session),
) -> AnnotationToolClientRead:
    """Update an annotation tool client."""

    return await annotation_tool_client_crud.update_annotation_tool_client(
        annotation_tool_client_id, annotation_tool_client_update, session
    )
