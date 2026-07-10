from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db(request: Request) -> AsyncSession:
    manager = request.app.state.db_manager
    async with manager.session_factory() as session:
        yield session
