from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """Create database tables."""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with SQLModel
        from app.models import (
            Project, Datapoint, Annotation, Model, ALMethod, AnnotationService
        )
        # These imports are needed to register the models with SQLModel
        _ = Project, Datapoint, Annotation, Model, ALMethod, AnnotationService
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        yield session
