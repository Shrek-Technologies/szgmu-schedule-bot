"""Integration test fixtures for database and DI container."""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from testcontainers.postgres import PostgresContainer

from di.providers.api_client import ApiProvider
from di.providers.config import ConfigProvider
from di.providers.database import DatabaseProvider
from di.providers.repositories import RepositoryProvider
from di.providers.services import ServiceProvider
from models.base import Base


def pytest_configure(config):
    """Set up Windows event loop policy before any tests run."""
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer]:
    """Start PostgreSQL 15-Alpine container for the entire test session."""
    container = PostgresContainer(image="postgres:17", driver="psycopg")

    # Windows testcontainers workaround: get_container_host_ip() returns wrong value
    if os.name == "nt":  # pragma: no cover
        container.get_container_host_ip = lambda: "localhost"  # type: ignore[assignment]

    container.start()
    yield container
    container.stop()


@pytest_asyncio.fixture(scope="session")
async def db_engine(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncEngine]:
    """Create async SQLAlchemy engine for PostgreSQL."""
    engine = create_async_engine(
        postgres_container.get_connection_url(),
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def setup_db_schema(db_engine: AsyncEngine) -> AsyncGenerator[None]:
    """Create database schema once per session using SQLAlchemy models."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="session")
def session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create session factory from engine."""
    return async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture
async def db_connection(
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection]:
    """
    Provide a database connection for each test within a savepoint.
    Changes are rolled back via savepoint rollback after the test.
    """
    async with db_engine.connect() as conn, conn.begin_nested():
        # Start a savepoint (nested transaction) for this test
        yield conn


@pytest_asyncio.fixture
async def async_session(
    db_connection: AsyncConnection,
) -> AsyncGenerator[AsyncSession]:
    """
    Provide an AsyncSession for each test within a transaction.
    All changes are rolled back via savepoint after the test.
    """
    session = AsyncSession(
        bind=db_connection,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def di_container(
    async_session: AsyncSession,
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncContainer]:
    """Create and configure Dishka DI container for tests.

    Overrides the session provider to use the test's async_session
    which is bound to a savepoint for transaction isolation.
    """
    old_env = {}
    env_vars = {
        "BOT_TOKEN": "999:TEST_TOKEN",
        "API_SCHEDULE_URL": "https://api.test/schedule",
        "REDIS_PASSWORD": "testpassword",
        "DB_HOST": postgres_container.get_container_host_ip(),
        "DB_PORT": str(postgres_container.get_exposed_port(5432)),
        "DB_USER": postgres_container.username,
        "DB_PASSWORD": postgres_container.password,
        "DB_DATABASE": postgres_container.dbname,
    }

    for key, value in env_vars.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Override session provider to use test's session instead of creating a new one
        class TestSessionProvider(Provider):
            @provide(scope=Scope.REQUEST)
            async def provide_session(self) -> AsyncSession:
                return async_session

        # Create container with test session provider
        # We exclude the default DatabaseProvider session and add our override
        container = make_async_container(
            ConfigProvider(),
            DatabaseProvider(),
            ApiProvider(),
            RepositoryProvider(),
            ServiceProvider(),
            TestSessionProvider(),  # Override the session provider
            AiogramProvider(),
        )
        yield container
    finally:
        for key, old_value in old_env.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value
