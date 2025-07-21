from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.database import get_session
from app.models import (
    Model, ModelCreate, ModelRead, ModelUpdate, Project
)

router = APIRouter()


@router.post("/", response_model=ModelRead, status_code=status.HTTP_201_CREATED)
async def create_model(
    model: ModelCreate,
    session: AsyncSession = Depends(get_session)
) -> ModelRead:
    """Create a new model."""
    # Check if project exists
    project_statement = select(Project).where(Project.id == model.project_id)
    project_result = await session.exec(project_statement)
    if not project_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_model = Model.model_validate(model)
    db_model.created_at = datetime.utcnow()
    
    session.add(db_model)
    await session.commit()
    await session.refresh(db_model)
    
    return ModelRead.model_validate(db_model)


@router.get("/", response_model=List[ModelRead])
async def get_models(
    project_id: int = None,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[ModelRead]:
    """Get all models, optionally filtered by project."""
    statement = select(Model)
    if project_id:
        statement = statement.where(Model.project_id == project_id)
    statement = statement.offset(skip).limit(limit)
    
    results = await session.exec(statement)
    models = results.all()
    
    return [ModelRead.model_validate(model) for model in models]


@router.get("/{model_id}", response_model=ModelRead)
async def get_model(
    model_id: int,
    session: AsyncSession = Depends(get_session)
) -> ModelRead:
    """Get a model by ID."""
    statement = select(Model).where(Model.id == model_id)
    result = await session.exec(statement)
    model = result.first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return ModelRead.model_validate(model)


@router.put("/{model_id}", response_model=ModelRead)
async def update_model(
    model_id: int,
    model_update: ModelUpdate,
    session: AsyncSession = Depends(get_session)
) -> ModelRead:
    """Update a model."""
    statement = select(Model).where(Model.id == model_id)
    result = await session.exec(statement)
    db_model = result.first()
    
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    model_data = model_update.model_dump(exclude_unset=True)
    for field, value in model_data.items():
        setattr(db_model, field, value)
    
    db_model.updated_at = datetime.utcnow()
    
    session.add(db_model)
    await session.commit()
    await session.refresh(db_model)
    
    return ModelRead.model_validate(db_model)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a model."""
    statement = select(Model).where(Model.id == model_id)
    result = await session.exec(statement)
    model = result.first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    await session.delete(model)
    await session.commit()


@router.post("/{model_id}/train", status_code=status.HTTP_200_OK)
async def train_model(
    model_id: int,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Train a model."""
    statement = select(Model).where(Model.id == model_id)
    result = await session.exec(statement)
    model = result.first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # TODO: Implement actual training logic
    return {"message": f"Training initiated for model {model.name}"}
