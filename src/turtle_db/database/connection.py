"""
Database connection management for SQLAlchemy with async support.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import logging

from turtle_db.config import settings

logger = logging.getLogger(__name__)

# Create the declarative base
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
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


async def create_tables():
    """Create all database tables."""
    from turtle_db.database.models import Base as ModelsBase
    
    async with engine.begin() as conn:
        # Drop all tables for fresh start (development only)
        # await conn.run_sync(ModelsBase.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(ModelsBase.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db_connection():
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")