from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.database import get_session
from app.models import (
    Datapoint, DatapointCreate, DatapointRead, DatapointUpdate, Project
)

router = APIRouter()


@router.post("/", response_model=DatapointRead, status_code=status.HTTP_201_CREATED)
async def create_datapoint(
    datapoint: DatapointCreate,
    session: AsyncSession = Depends(get_session)
) -> DatapointRead:
    """Create a new datapoint."""
    # Check if project exists
    project_statement = select(Project).where(Project.id == datapoint.project_id)
    project_result = await session.exec(project_statement)
    if not project_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_datapoint = Datapoint.model_validate(datapoint)
    db_datapoint.created_at = datetime.utcnow()
    
    session.add(db_datapoint)
    await session.commit()
    await session.refresh(db_datapoint)
    
    return DatapointRead.model_validate(db_datapoint)


@router.get("/", response_model=List[DatapointRead])
async def get_datapoints(
    project_id: int = None,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[DatapointRead]:
    """Get all datapoints, optionally filtered by project."""
    statement = select(Datapoint)
    if project_id:
        statement = statement.where(Datapoint.project_id == project_id)
    statement = statement.offset(skip).limit(limit)
    
    results = await session.exec(statement)
    datapoints = results.all()
    
    return [DatapointRead.model_validate(datapoint) for datapoint in datapoints]


@router.get("/{datapoint_id}", response_model=DatapointRead)
async def get_datapoint(
    datapoint_id: int,
    session: AsyncSession = Depends(get_session)
) -> DatapointRead:
    """Get a datapoint by ID."""
    statement = select(Datapoint).where(Datapoint.id == datapoint_id)
    result = await session.exec(statement)
    datapoint = result.first()
    
    if not datapoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datapoint not found"
        )
    
    return DatapointRead.model_validate(datapoint)


@router.put("/{datapoint_id}", response_model=DatapointRead)
async def update_datapoint(
    datapoint_id: int,
    datapoint_update: DatapointUpdate,
    session: AsyncSession = Depends(get_session)
) -> DatapointRead:
    """Update a datapoint."""
    statement = select(Datapoint).where(Datapoint.id == datapoint_id)
    result = await session.exec(statement)
    db_datapoint = result.first()
    
    if not db_datapoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datapoint not found"
        )
    
    datapoint_data = datapoint_update.model_dump(exclude_unset=True)
    for field, value in datapoint_data.items():
        setattr(db_datapoint, field, value)
    
    db_datapoint.updated_at = datetime.utcnow()
    
    session.add(db_datapoint)
    await session.commit()
    await session.refresh(db_datapoint)
    
    return DatapointRead.model_validate(db_datapoint)


@router.delete("/{datapoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_datapoint(
    datapoint_id: int,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a datapoint."""
    statement = select(Datapoint).where(Datapoint.id == datapoint_id)
    result = await session.exec(statement)
    datapoint = result.first()
    
    if not datapoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datapoint not found"
        )
    
    await session.delete(datapoint)
    await session.commit()
