"""Project API routes.

This module contains all the endpoints for managing projects in the Active Annotate API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.database import get_session
from app.models.project import Project, ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, session: AsyncSession = Depends(get_session)
) -> ProjectRead:
    """Create a new project."""
    db_project = Project.model_validate(project)

    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)

    return ProjectRead.model_validate(db_project)


@router.get("/", response_model=List[ProjectRead])
async def get_projects(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
) -> List[ProjectRead]:
    """Get all projects."""
    statement = select(Project).offset(skip).limit(limit)
    results = await session.execute(statement)
    projects = results.scalars().all()

    return [ProjectRead.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> ProjectRead:
    """Get a project by ID."""
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return ProjectRead.model_validate(project)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    """Update a project."""
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    db_project = result.scalars().first()

    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    project_data = project_update.model_dump(exclude_unset=True)
    for field, value in project_data.items():
        setattr(db_project, field, value)

    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)

    return ProjectRead.model_validate(db_project)


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
