from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.database import get_session
from app.models import (
    AnnotationService, AnnotationServiceCreate, AnnotationServiceRead, AnnotationServiceUpdate
)

router = APIRouter()


@router.post("/", response_model=AnnotationServiceRead, status_code=status.HTTP_201_CREATED)
async def create_annotation_service(
    annotation_service: AnnotationServiceCreate,
    session: AsyncSession = Depends(get_session)
) -> AnnotationServiceRead:
    """Create a new annotation service."""
    db_annotation_service = AnnotationService.model_validate(annotation_service)
    db_annotation_service.created_at = datetime.utcnow()
    
    session.add(db_annotation_service)
    await session.commit()
    await session.refresh(db_annotation_service)
    
    return AnnotationServiceRead.model_validate(db_annotation_service)


@router.get("/", response_model=List[AnnotationServiceRead])
async def get_annotation_services(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[AnnotationServiceRead]:
    """Get all annotation services."""
    statement = select(AnnotationService).offset(skip).limit(limit)
    results = await session.exec(statement)
    annotation_services = results.all()
    
    return [AnnotationServiceRead.model_validate(service) for service in annotation_services]


@router.get("/{service_id}", response_model=AnnotationServiceRead)
async def get_annotation_service(
    service_id: int,
    session: AsyncSession = Depends(get_session)
) -> AnnotationServiceRead:
    """Get an annotation service by ID."""
    statement = select(AnnotationService).where(AnnotationService.id == service_id)
    result = await session.exec(statement)
    annotation_service = result.first()
    
    if not annotation_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation service not found"
        )
    
    return AnnotationServiceRead.model_validate(annotation_service)


@router.put("/{service_id}", response_model=AnnotationServiceRead)
async def update_annotation_service(
    service_id: int,
    service_update: AnnotationServiceUpdate,
    session: AsyncSession = Depends(get_session)
) -> AnnotationServiceRead:
    """Update an annotation service."""
    statement = select(AnnotationService).where(AnnotationService.id == service_id)
    result = await session.exec(statement)
    db_service = result.first()
    
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation service not found"
        )
    
    service_data = service_update.model_dump(exclude_unset=True)
    for field, value in service_data.items():
        setattr(db_service, field, value)
    
    db_service.updated_at = datetime.utcnow()
    
    session.add(db_service)
    await session.commit()
    await session.refresh(db_service)
    
    return AnnotationServiceRead.model_validate(db_service)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation_service(
    service_id: int,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete an annotation service."""
    statement = select(AnnotationService).where(AnnotationService.id == service_id)
    result = await session.exec(statement)
    annotation_service = result.first()
    
    if not annotation_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation service not found"
        )
    
    await session.delete(annotation_service)
    await session.commit()


@router.post("/{service_id}/add-annotation", status_code=status.HTTP_200_OK)
async def add_annotation_to_service(
    service_id: int,
    annotation_data: dict,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Add annotation via the annotation service."""
    statement = select(AnnotationService).where(AnnotationService.id == service_id)
    result = await session.exec(statement)
    annotation_service = result.first()
    
    if not annotation_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation service not found"
        )
    
    # TODO: Implement actual annotation service integration
    return {"message": f"Annotation added via {annotation_service.service_type}", "data": annotation_data}


@router.post("/{service_id}/get-preannotation", status_code=status.HTTP_200_OK)
async def get_preannotation_from_service(
    service_id: int,
    data: dict,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Get preannotation from the annotation service."""
    statement = select(AnnotationService).where(AnnotationService.id == service_id)
    result = await session.exec(statement)
    annotation_service = result.first()
    
    if not annotation_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation service not found"
        )
    
    # TODO: Implement actual preannotation logic
    return {"preannotation": "sample_preannotation", "service": annotation_service.service_type, "input_data": data}
