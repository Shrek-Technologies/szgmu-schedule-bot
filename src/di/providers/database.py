from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from core.config import DatabaseSettings


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_engine(self, db_settings: DatabaseSettings) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            db_settings.dsn,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def provide_session_factory(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
