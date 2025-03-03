from __future__ import annotations

from typing import AsyncGenerator

# Upsert constructs are not dialect agnostic
# Dialect-specific imports below act as an entrypoint from which other modules can import the upsert construct
from sqlalchemy.dialects.sqlite import insert as dialect_upsert  # noqa: F401
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.schemas.database as db
from config import get_config

engine = create_async_engine(get_config().DATABASE_URI)
async_session = async_sessionmaker(bind=engine, autocommit=False, autoflush=True)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency injection function to pass a db session into endpoints.

    FastAPI internally wraps this function into an async context manager, so it cannot
    be used as a context manager itself.
    """
    async with async_session() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_db_tables(engine: AsyncEngine, recreate: bool = False) -> None:
    async with engine.begin() as conn:  # `engine.begin()` due to a synchronous DB commands
        if recreate:
            await conn.run_sync(db.Base.metadata.drop_all)
        await conn.run_sync(db.Base.metadata.create_all)
