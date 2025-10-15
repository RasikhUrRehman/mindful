from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReminderBase(BaseModel):
    """Base reminder schema."""
    reminder_type: str = Field(..., description="habit, meditation, exercise, mindful_eating, break, or custom")
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    trigger_time: datetime
    frequency: Optional[str] = None


class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""
    pass


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""
    reminder_type: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    trigger_time: Optional[datetime] = None
    frequency: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class ReminderResponse(ReminderBase):
    """Schema for reminder responses."""
    id: int
    user_id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TimerRequest(BaseModel):
    """Schema for timer requests."""
    timer_type: str = Field(..., description="meditation, exercise, mindful_eating, break, or custom")
    duration_seconds: int = Field(..., gt=0, description="Timer duration in seconds")
    title: Optional[str] = None
