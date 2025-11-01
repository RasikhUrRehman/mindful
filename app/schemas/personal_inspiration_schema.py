from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PersonalInspirationBase(BaseModel):
    """Base personal inspiration schema."""
    inspiration: str = Field(..., min_length=1)


class PersonalInspirationCreate(PersonalInspirationBase):
    """Schema for creating a new personal inspiration."""
    pass


class PersonalInspirationUpdate(BaseModel):
    """Schema for updating a personal inspiration."""
    inspiration: Optional[str] = Field(None, min_length=1)


class PersonalInspirationResponse(PersonalInspirationBase):
    """Schema for personal inspiration responses."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
