"""Initialize database with Alembic migrations"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base


async def init_db():
    """Create all database tables"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())

