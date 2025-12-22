"""User schemas"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    privacy_consent: bool = True
    anonymous_token: Optional[str] = None  # For converting anonymous to registered


class AnonymousSessionCreate(BaseModel):
    """Anonymous session creation"""
    privacy_consent: bool = True


class UserLogin(BaseModel):
    """User login schema"""
    identifier: str = Field(..., description="Username or email")
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    username: str
    email: Optional[str] = None
    is_anonymous: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse  # No quotes needed now


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
