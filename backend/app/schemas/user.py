"""User schemas"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[str] = None
