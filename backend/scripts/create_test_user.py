"""Create a test user for development"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


async def create_test_user():
    """Create a test user"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "testuser"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True
        )
        
        session.add(test_user)
        await session.commit()
        
        print("Test user created successfully!")
        print(f"Username: testuser")
        print(f"Password: testpassword123")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_test_user())

