from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    gender: Optional[str] = None
    motivations: Optional[str] = None
    language: str = "en"
    picture: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = None
    gender: Optional[str] = None
    motivations: Optional[str] = None
    language: Optional[str] = None
    picture: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses."""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """Extended user profile response."""
    pass
