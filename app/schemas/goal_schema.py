from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GoalBase(BaseModel):
    """Base goal schema."""
    title: str = Field(..., min_length=1, max_length=255)
    goal_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    timeframe: str = Field(..., description="short-term, long-term, etc.")


class GoalCreate(GoalBase):
    """Schema for creating a new goal."""
    pass


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    title: Optional[str] = None
    goal_type: Optional[str] = None
    description: Optional[str] = None
    timeframe: Optional[str] = None
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_completed: Optional[bool] = None


class GoalResponse(GoalBase):
    """Schema for goal responses."""
    id: int
    user_id: int
    completion_percentage: float
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
