from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HabitBase(BaseModel):
    """Base habit schema."""
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., description="daily, weekly, or monthly")
    description: Optional[str] = None


class HabitCreate(HabitBase):
    """Schema for creating a new habit."""
    pass


class HabitUpdate(BaseModel):
    """Schema for updating a habit."""
    title: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    description: Optional[str] = None
    streak_count: Optional[int] = None
    success_rate: Optional[float] = None
    is_active: Optional[bool] = None


class HabitResponse(HabitBase):
    """Schema for habit responses."""
    id: int
    user_id: int
    streak_count: int
    success_rate: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
