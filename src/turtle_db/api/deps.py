"""
Dependencies for FastAPI endpoints.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from turtle_db.database.connection import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()