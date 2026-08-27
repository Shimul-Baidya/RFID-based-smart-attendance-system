"""Provide shared SQLAlchemy database configuration."""

import os
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Serve as the base class for all database models."""


@lru_cache
def _create_engine(database_url: str) -> Engine:
    """Create and cache the shared SQLAlchemy engine.

    Args:
        database_url: SQLAlchemy-compatible database connection URL.

    Returns:
        Configured SQLAlchemy engine.
    """
    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def get_database() -> Generator[Session, None, None]:
    """Provide one database session for a FastAPI request.

    Yields:
        Active SQLAlchemy database session.

    Raises:
        RuntimeError: If ``DATABASE_URL`` is not configured.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not configured.")

    engine = _create_engine(database_url)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    database = session_factory()

    try:
        yield database
    finally:
        database.close()
