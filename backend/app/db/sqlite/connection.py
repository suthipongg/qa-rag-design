from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


class SQLiteManager:
    def __init__(self, database_url: str, debug: bool = False):
        async_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        self.engine = create_async_engine(async_url, echo=debug)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            from app.db.sqlite.models import Base
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()


def init_db_manager(database_url: str, debug: bool = False) -> SQLiteManager:
    return SQLiteManager(database_url, debug)



