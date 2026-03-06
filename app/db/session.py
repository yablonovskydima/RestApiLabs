from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session