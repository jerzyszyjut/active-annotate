from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.database import get_session
from app.models import (
    ALMethod, ALMethodCreate, ALMethodRead, ALMethodUpdate, Project
)

router = APIRouter()


@router.post("/", response_model=ALMethodRead, status_code=status.HTTP_201_CREATED)
async def create_al_method(
    al_method: ALMethodCreate,
    session: AsyncSession = Depends(get_session)
) -> ALMethodRead:
    """Create a new AL method."""
    # Check if project exists
    project_statement = select(Project).where(Project.id == al_method.project_id)
    project_result = await session.exec(project_statement)
    if not project_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_al_method = ALMethod.model_validate(al_method)
    db_al_method.created_at = datetime.utcnow()
    
    session.add(db_al_method)
    await session.commit()
    await session.refresh(db_al_method)
    
    return ALMethodRead.model_validate(db_al_method)


@router.get("/", response_model=List[ALMethodRead])
async def get_al_methods(
    project_id: int = None,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[ALMethodRead]:
    """Get all AL methods, optionally filtered by project."""
    statement = select(ALMethod)
    if project_id:
        statement = statement.where(ALMethod.project_id == project_id)
    statement = statement.offset(skip).limit(limit)
    
    results = await session.exec(statement)
    al_methods = results.all()
    
    return [ALMethodRead.model_validate(al_method) for al_method in al_methods]


@router.get("/{al_method_id}", response_model=ALMethodRead)
async def get_al_method(
    al_method_id: int,
    session: AsyncSession = Depends(get_session)
) -> ALMethodRead:
    """Get an AL method by ID."""
    statement = select(ALMethod).where(ALMethod.id == al_method_id)
    result = await session.exec(statement)
    al_method = result.first()
    
    if not al_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AL method not found"
        )
    
    return ALMethodRead.model_validate(al_method)


@router.put("/{al_method_id}", response_model=ALMethodRead)
async def update_al_method(
    al_method_id: int,
    al_method_update: ALMethodUpdate,
    session: AsyncSession = Depends(get_session)
) -> ALMethodRead:
    """Update an AL method."""
    statement = select(ALMethod).where(ALMethod.id == al_method_id)
    result = await session.exec(statement)
    db_al_method = result.first()
    
    if not db_al_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AL method not found"
        )
    
    al_method_data = al_method_update.model_dump(exclude_unset=True)
    for field, value in al_method_data.items():
        setattr(db_al_method, field, value)
    
    db_al_method.updated_at = datetime.utcnow()
    
    session.add(db_al_method)
    await session.commit()
    await session.refresh(db_al_method)
    
    return ALMethodRead.model_validate(db_al_method)


@router.delete("/{al_method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_al_method(
    al_method_id: int,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete an AL method."""
    statement = select(ALMethod).where(ALMethod.id == al_method_id)
    result = await session.exec(statement)
    al_method = result.first()
    
    if not al_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AL method not found"
        )
    
    await session.delete(al_method)
    await session.commit()


@router.post("/{al_method_id}/calculate-score", status_code=status.HTTP_200_OK)
async def calculate_score(
    al_method_id: int,
    annotation_data: dict,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Calculate score for an annotation using the AL method."""
    statement = select(ALMethod).where(ALMethod.id == al_method_id)
    result = await session.exec(statement)
    al_method = result.first()
    
    if not al_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AL method not found"
        )
    
    # TODO: Implement actual score calculation logic based on AL method
    return {"score": 0.85, "method": al_method.name, "annotation": annotation_data}
