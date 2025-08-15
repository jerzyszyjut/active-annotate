from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.active_learning_client import ActiveLearningClient
from app.schemas.active_learning_client import (
    ActiveLearningClientCreate,
    ActiveLearningClientRead,
    ActiveLearningClientUpdate
)


class ActiveLearningClientCRUD:
    async def create_active_learning_client(
        self, active_learning_client: ActiveLearningClientCreate, session: AsyncSession
    ) -> ActiveLearningClientRead:
        db_active_learning_client = ActiveLearningClient.model_validate(
            active_learning_client
        )

        session.add(db_active_learning_client)
        await session.commit()
        await session.refresh(db_active_learning_client)

        return ActiveLearningClientRead.model_validate(db_active_learning_client)

    async def get_active_learning_clients(
        self, skip: int, limit: int, session: AsyncSession
    ) -> list[ActiveLearningClientRead]:
        statement = select(ActiveLearningClient).offset(skip).limit(limit)
        results = await session.execute(statement)
        active_learning_clients = results.scalars().all()

        return [
            ActiveLearningClientRead.model_validate(client)
            for client in active_learning_clients
        ]

    async def get_active_learning_client_by_id(
        self, active_learning_client_id: int, session: AsyncSession
    ) -> ActiveLearningClientRead:
        statement = select(ActiveLearningClient).where(
            ActiveLearningClient.id == active_learning_client_id
        )
        result = await session.execute(statement)
        client = result.scalars().first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active learning client not found",
            )

        return ActiveLearningClientRead.model_validate(client)

    async def update_active_learning_client(
        self,
        active_learning_client_id: int,
        active_learning_client_update: ActiveLearningClientUpdate,
        session: AsyncSession,
    ) -> ActiveLearningClientRead:
        statement = select(ActiveLearningClient).where(
            ActiveLearningClient.id == active_learning_client_id
        )
        result = await session.execute(statement)
        db_client = result.scalars().first()

        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active learning client not found",
            )

        update_data = active_learning_client_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_client, field, value)

        session.add(db_client)
        await session.commit()
        await session.refresh(db_client)

        return ActiveLearningClientRead.model_validate(db_client)
