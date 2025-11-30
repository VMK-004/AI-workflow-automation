"""Authentication service"""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if username already exists
        existing_user = await AuthService.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = await AuthService.get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        """Authenticate user by username and password"""
        user = await AuthService.get_user_by_username(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str | UUID) -> User | None:
        """Get user by ID"""
        # Keep as string for SQLite compatibility (id is now String(36), not UUID)
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        """Get user by username"""
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user
