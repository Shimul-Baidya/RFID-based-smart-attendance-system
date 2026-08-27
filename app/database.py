"""Asynchronous SQLAlchemy database session configuration."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield one database session for a request.

    Yields:
        An asynchronous SQLAlchemy session.
    """

    async with SessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
