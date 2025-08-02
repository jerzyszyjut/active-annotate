"""Project API routes.

This module contains all the endpoints for managing projects in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.crud.annotation_tool_client import AnnotationToolClientCRUD
from app.db.database import get_session
from app.models.annotation_tool_client import AnnotationToolClient

from app.schemas.annotation_tool_client import (
    AnnotationToolClientCreate,
    AnnotationToolClientRead,
    AnnotationToolClientUpdate
)


router = APIRouter(prefix="/annotation-tool-client", tags=["annotation_tool_client"])
annotation_tool_client_crud = AnnotationToolClientCRUD()

@router.post("/", response_model=AnnotationToolClientRead, status_code=status.HTTP_201_CREATED)
async def create_annotation_tool_client(
    annotation_tool_client: AnnotationToolClientCreate,
    session: AsyncSession = Depends(get_session)
) -> AnnotationToolClientRead:
    """Create a new annotation tool client."""

    return await annotation_tool_client_crud.create_annotation_tool(annotation_tool_client, session)