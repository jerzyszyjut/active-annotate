"""Project API routes.

This module contains all the endpoints for managing projects in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.crud.project import ProjectCRUD
from app.db.database import get_session
from app.models.project import Project

from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate


router = APIRouter(prefix="/projects", tags=["projects"])
project_crud = ProjectCRUD()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, session: AsyncSession = Depends(get_session)
) -> ProjectRead:
    """Create a new project."""

    return await project_crud.create(project, session)


@router.get("/", response_model=List[ProjectRead])
async def get_projects(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
) -> List[ProjectRead]:
    """Get all projects."""

    return await project_crud.get_projects(skip, limit, session)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> ProjectRead:
    """Get a project by ID."""

    return await project_crud.get_project_by_id(project_id, session)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    """Update a project."""

    return await project_crud.update_project(project_id, project_update, session)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a project."""
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    await session.delete(project)
    await session.commit()
