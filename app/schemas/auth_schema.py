from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login requests."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Schema for token responses."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutResponse(BaseModel):
    """Schema for logout responses."""
    message: str


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication."""
    id_token: str = Field(..., description="Google ID token from client")


class GoogleAuthResponse(BaseModel):
    """Schema for Google OAuth response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    is_new_user: bool = Field(default=False, description="True if this is a newly created user")


# Schemas package
