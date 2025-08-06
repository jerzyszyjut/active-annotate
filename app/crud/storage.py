from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.storage import Storage
from app.schemas.storage import (
    StorageCreate,
    StorageRead,
    StorageUpdate
)


class StorageCRUD:
    async def create(self, storage: StorageCreate, session: AsyncSession) -> StorageRead:
        db_storage = Storage.model_validate(storage)

        session.add(db_storage)

        await session.commit()
        await session.refresh(db_storage)

        return StorageRead.model_validate(db_storage)
    
    async def get_storages(self, skip, limit, session: AsyncSession) -> list[StorageRead]:
        statement = select(Storage).offset(skip).limit(limit)
        results = await session.execute(statement)
        storages = results.scalars().all()

        return [StorageRead.model_validate(storage) for storage in storages]

    async def get_storage_by_id(self, storage_id: int, session: AsyncSession) -> StorageRead:
        statement = select(Storage).where(Storage.id == storage_id)
        result = await session.execute(statement)
        storage = result.scalars().first()

        if not storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Storage not found"
            )

        return StorageRead.model_validate(storage)

    async def update_storage(
        self,
        storage_id: int,
        storage_update: StorageUpdate,
        session: AsyncSession
    ) -> StorageRead:
        statement = select(Storage).where(Storage.id == storage_id)
        result = await session.execute(statement)
        db_storage = result.scalars().first()

        if not db_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Storage not found"
            )

        project_data = storage_update.model_dump(exclude_unset=True)
        for field, value in project_data.items():
            setattr(db_storage, field, value)

        session.add(db_storage)
        await session.commit()
        await session.refresh(db_storage)

        return StorageRead.model_validate(db_storage)
