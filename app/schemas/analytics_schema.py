from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AnalyticsBase(BaseModel):
    """Base analytics schema."""
    period: str = Field(..., description="daily, weekly, or monthly")


class AnalyticsSummary(BaseModel):
    """Schema for analytics summary."""
    summary: str
    score: float = Field(..., ge=0, le=100)
    mood_average: Optional[str]
    habit_completion_rate: Optional[float]
    goal_progress: Optional[float]
    insights: Optional[str]
    period: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProgressResponse(BaseModel):
    """Schema for progress response combining multiple analytics."""
    overall_score: float
    mood_data: Dict[str, Any]
    habits_data: Dict[str, Any]
    goals_data: Dict[str, Any]
    insights: str
    generated_at: datetime
