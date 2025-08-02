from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate
)


class ProjectCRUD:
    async def create(self, project: ProjectCreate, session: AsyncSession) -> ProjectRead:
        db_project = Project.model_validate(project)
        
        session.add(db_project)
        
        await session.commit()
        await session.refresh(db_project)

        return ProjectRead.model_validate(db_project)
    
    async def get_projects(self, skip, limit, session: AsyncSession) -> list[ProjectRead]:
        statement = select(Project).offset(skip).limit(limit)
        results = await session.execute(statement)
        projects = results.scalars().all()

        return [ProjectRead.model_validate(project) for project in projects]

    async def get_project_by_id(self, project_id: int, session: AsyncSession) -> ProjectRead:
        statement = select(Project).where(Project.id == project_id)
        result = await session.execute(statement)
        project = result.scalars().first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        return ProjectRead.model_validate(project)