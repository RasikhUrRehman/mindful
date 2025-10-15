from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MoodBase(BaseModel):
    """Base mood schema."""
    mood_type: str = Field(..., description="excellent, good, neutral, sad, anxious, or angry")
    intensity: Optional[int] = Field(None, ge=1, le=10, description="1-10 scale")
    note: Optional[str] = None


class MoodCreate(MoodBase):
    """Schema for creating a new mood entry."""
    pass


class MoodUpdate(BaseModel):
    """Schema for updating a mood entry."""
    mood_type: Optional[str] = None
    intensity: Optional[int] = Field(None, ge=1, le=10)
    note: Optional[str] = None


class MoodResponse(MoodBase):
    """Schema for mood responses."""
    id: int
    user_id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class MoodSummary(BaseModel):
    """Schema for mood summary statistics."""
    period: str  # daily, weekly, monthly
    average_mood: str
    average_intensity: Optional[float]
    most_common_mood: str
    total_entries: int
    mood_breakdown: dict  # mood_type -> count
