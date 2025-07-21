from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.database import get_session
from app.models import (
    Annotation, AnnotationCreate, AnnotationRead, AnnotationUpdate, Datapoint
)

router = APIRouter()


@router.post("/", response_model=AnnotationRead, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    annotation: AnnotationCreate,
    session: AsyncSession = Depends(get_session)
) -> AnnotationRead:
    """Create a new annotation."""
    # Check if datapoint exists
    datapoint_statement = select(Datapoint).where(Datapoint.id == annotation.datapoint_id)
    datapoint_result = await session.exec(datapoint_statement)
    if not datapoint_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datapoint not found"
        )
    
    db_annotation = Annotation.model_validate(annotation)
    db_annotation.created_at = datetime.utcnow()
    
    session.add(db_annotation)
    await session.commit()
    await session.refresh(db_annotation)
    
    return AnnotationRead.model_validate(db_annotation)


@router.get("/", response_model=List[AnnotationRead])
async def get_annotations(
    datapoint_id: int = None,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[AnnotationRead]:
    """Get all annotations, optionally filtered by datapoint."""
    statement = select(Annotation)
    if datapoint_id:
        statement = statement.where(Annotation.datapoint_id == datapoint_id)
    statement = statement.offset(skip).limit(limit)
    
    results = await session.exec(statement)
    annotations = results.all()
    
    return [AnnotationRead.model_validate(annotation) for annotation in annotations]


@router.get("/{annotation_id}", response_model=AnnotationRead)
async def get_annotation(
    annotation_id: int,
    session: AsyncSession = Depends(get_session)
) -> AnnotationRead:
    """Get an annotation by ID."""
    statement = select(Annotation).where(Annotation.id == annotation_id)
    result = await session.exec(statement)
    annotation = result.first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    return AnnotationRead.model_validate(annotation)


@router.put("/{annotation_id}", response_model=AnnotationRead)
async def update_annotation(
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    session: AsyncSession = Depends(get_session)
) -> AnnotationRead:
    """Update an annotation."""
    statement = select(Annotation).where(Annotation.id == annotation_id)
    result = await session.exec(statement)
    db_annotation = result.first()
    
    if not db_annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    annotation_data = annotation_update.model_dump(exclude_unset=True)
    for field, value in annotation_data.items():
        setattr(db_annotation, field, value)
    
    db_annotation.updated_at = datetime.utcnow()
    
    session.add(db_annotation)
    await session.commit()
    await session.refresh(db_annotation)
    
    return AnnotationRead.model_validate(db_annotation)


@router.delete("/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: int,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete an annotation."""
    statement = select(Annotation).where(Annotation.id == annotation_id)
    result = await session.exec(statement)
    annotation = result.first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    await session.delete(annotation)
    await session.commit()
