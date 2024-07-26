from __future__ import annotations

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import create_app
from config import Config, get_config
from src.database import get_db_session, recreate_database

test_engine = create_async_engine(get_config().DATABASE_URI)
test_async_session = async_sessionmaker(
    bind=test_engine, autocommit=False, autoflush=True
)


def get_test_config() -> Config:
    return Config(
        SQLALCHEMY_DATABASE_URI='sqlite+aiosqlite:///internal.db',
    )


async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency injection function to pass a db session into endpoints.

    FastAPI internally wraps this function into an async context manager, so it cannot
    be used as a context manager itself.
    """
    await recreate_database()
    async with test_async_session() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture(autouse=True)
async def db() -> None:
    await recreate_database(test_engine)


@pytest.fixture()
def test_app() -> FastAPI:
    test_app = create_app()

    test_app.dependency_overrides[get_config] = get_test_config
    test_app.dependency_overrides[get_db_session] = get_test_db_session
    return test_app


@pytest.fixture()
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


# @pytest.fixture()
# def db_entity_factory() -> DbEntityFactory:
#     return DbEntityFactory()
