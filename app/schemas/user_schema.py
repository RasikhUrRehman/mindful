from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    gender: Optional[str] = None
    motivations: Optional[str] = None
    language: str = "en"
    picture: Optional[str] = None
    user_goals: Optional[List[Any]] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: Optional[str] = Field(None, min_length=8)  # Optional for OAuth users


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = None
    gender: Optional[str] = None
    motivations: Optional[str] = None
    language: Optional[str] = None
    picture: Optional[str] = None
    user_goals: Optional[List[Any]] = None
    fcm_token: Optional[str] = None


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


class ProfileUpdateResponse(BaseModel):
    """Response for profile update."""
    success: bool
    message: str
    user: UserResponse
    
    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    
    
class ChangePasswordResponse(BaseModel):
    """Schema for change password response."""
    message: str


class FCMTokenUpdate(BaseModel):
    """Schema for updating FCM token."""
    fcm_token: str = Field(..., min_length=1)
    device_timestamp: Optional[str] = None  # ISO format timestamp from device


class FCMTokenResponse(BaseModel):
    """Schema for FCM token update response."""
    success: bool
    message: str
