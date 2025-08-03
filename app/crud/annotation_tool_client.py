from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.annotation_tool_client import AnnotationToolClient
from app.schemas.annotation_tool_client import (
    AnnotationToolClientCreate,
    AnnotationToolClientRead,
    AnnotationToolClientUpdate
)


class AnnotationToolClientCRUD:
    async def create_annotation_tool(
            self,
            annotation_tool_client: AnnotationToolClientCreate,
            session: AsyncSession
        ) -> AnnotationToolClientRead:
        db_annotation_tool_client = AnnotationToolClient.model_validate(annotation_tool_client)

        session.add(db_annotation_tool_client)

        await session.commit()
        await session.refresh(db_annotation_tool_client)

        return AnnotationToolClientRead.model_validate(db_annotation_tool_client)

    async def get_annotation_tool_clients(self, skip: int, limit: int, session: AsyncSession) -> list[AnnotationToolClientRead]:
        statement = select(AnnotationToolClient).offset(skip).limit(limit)
        results = await session.execute(statement)
        annotation_tool_clients = results.scalars().all()

        return [AnnotationToolClientRead.model_validate(annotation_tool_client) for annotation_tool_client in annotation_tool_clients]

    async def get_at_client_by_ip_address_and_project_id(self, at_client_ip_address: str, at_client_project_id: int, session: AsyncSession) -> AnnotationToolClientRead:
        statement = select(AnnotationToolClient).where(
            and_(
                AnnotationToolClient.ip_address == at_client_ip_address,
                AnnotationToolClient.ls_project_id == at_client_project_id
            )
        )
        result = await session.execute(statement)
        annotation_tool_clients = result.scalars().first()

        if not annotation_tool_clients:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Annotation tool client not found"
            )

        return AnnotationToolClientRead.model_validate(annotation_tool_clients)

    async def get_annotation_tool_client_by_id(self, annotation_tool_client_id: int, session: AsyncSession) -> AnnotationToolClientRead:
        statement = select(AnnotationToolClient).where(AnnotationToolClient.id == annotation_tool_client_id)
        result = await session.execute(statement)
        annotation_tool_clients = result.scalars().first()

        if not annotation_tool_clients:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Annotation tool client not found"
            )

        return AnnotationToolClientRead.model_validate(annotation_tool_clients)

    async def update_annotation_tool_client(
            self,
            annotation_tool_client_id: int,
            annotation_tool_client_update: AnnotationToolClientUpdate,
            session: AsyncSession
        ) -> AnnotationToolClientRead:
            statement = select(AnnotationToolClient).where(
                 AnnotationToolClient.id == annotation_tool_client_id
            )
            result = await session.execute(statement)
            db_annotation_tool_client = result.scalars().first()

            if not db_annotation_tool_client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Annotation tool client not found"
                )

            annotation_tool_client_data = annotation_tool_client_update.model_dump(exclude_unset=True)
            for field, value in annotation_tool_client_data.items():
                setattr(db_annotation_tool_client, field, value)

            session.add(db_annotation_tool_client)
            await session.commit()
            await session.refresh(db_annotation_tool_client)

            return AnnotationToolClientRead.model_validate(db_annotation_tool_client)