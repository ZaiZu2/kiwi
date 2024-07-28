from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import create_app
from config import Config, get_config
from src.database import get_db_session, create_db_tables

pytest_plugins = ("pytest_asyncio",)

test_engine = create_async_engine(get_config().DATABASE_URI)
test_async_session = async_sessionmaker(
    bind=test_engine, autocommit=False, autoflush=True
)


def get_test_config() -> Config:
    return Config(
        SQLALCHEMY_DATABASE_URI='sqlite+aiosqlite:///tests/internal.db',
    )


async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency injection function to pass a db session into endpoints.

    FastAPI internally wraps this function into an async context manager, so it cannot
    be used as a context manager itself.
    """
    async with test_async_session() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Open a DB session for a test case."""
    async with test_async_session() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture()
async def test_app() -> FastAPI:
    test_app = create_app()
    test_app.dependency_overrides[get_config] = get_test_config
    test_app.dependency_overrides[get_db_session] = get_test_db_session

    await create_db_tables(test_engine)
    return test_app


@pytest.fixture()
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        app=test_app, base_url='http://localhost:8000/api'
    ) as test_client:
        yield test_client


@pytest.fixture(scope='session')
def countries_input():
    """
    Input file contains 5 different ISO codes with 5 country names assigned to each.
    `CAN` code has 5 names, but 3 are duplicates.
    """
    with open(Path('tests/test_input.json')) as file:
        return json.load(file)


@pytest.fixture()
async def _populate_db(countries_input: str, client: AsyncClient) -> None:
    """Helper fixture to populate the DB with test data."""
    with open(Path('tests/test_input.json')) as file:
        await client.post('/countries', json=json.load(file))
