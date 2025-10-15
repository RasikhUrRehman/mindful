from pydantic import BaseModel, EmailStr, Field


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


# Schemas package
