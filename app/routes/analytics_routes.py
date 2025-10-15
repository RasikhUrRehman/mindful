from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics_schema import ProgressResponse, AnalyticsSummary
from app.services.analytics_service import AnalyticsService
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/analytics", tags=["analytics"])



@router.get("/progress/summary", response_model=ProgressResponse)
def get_progress_summary(
    period: str = "weekly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive progress summary for the user.

    - **period**: 'daily', 'weekly', or 'monthly'
    """
    user = current_user
    
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be 'daily', 'weekly', or 'monthly'",
        )
    
    # Get summary data
    summary_data = AnalyticsService.get_user_summary(db, user.id, period)
    
    # Get mood breakdown
    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)
    mood_breakdown = AnalyticsService.get_mood_breakdown(db, user.id, days)
    
    # Get habit stats
    habit_stats = AnalyticsService.get_habit_stats(db, user.id)
    
    return ProgressResponse(
        overall_score=summary_data["overall_score"],
        mood_data={
            "average": summary_data["mood_average"],
            "breakdown": mood_breakdown,
            "entries": summary_data["mood_count"],
        },
        habits_data={
            "total": habit_stats["total"],
            "active": habit_stats["active"],
            "avg_streak": habit_stats["avg_streak"],
            "avg_success_rate": habit_stats["avg_success_rate"],
        },
        goals_data={
            "progress": summary_data["goal_progress"],
        },
        insights=summary_data["insights"],
        generated_at=datetime.utcnow(),
    )


@router.get("/mood/summary", response_model=Dict[str, Any])
def get_mood_analytics(
    period: str = "weekly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get mood analytics for a specific period."""
    user = current_user
    
    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)
    mood_breakdown = AnalyticsService.get_mood_breakdown(db, user.id, days)
    
    return {
        "period": period,
        "breakdown": mood_breakdown,
        "generated_at": datetime.utcnow(),
    }


@router.get("/habits/stats", response_model=Dict[str, Any])
def get_habit_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get habit statistics."""
    user = current_user
    
    stats = AnalyticsService.get_habit_stats(db, user.id)
    
    return {
        **stats,
        "generated_at": datetime.utcnow(),
    }


@router.post("/save-summary")
def save_summary(
    period: str = "weekly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save analytics summary to database."""
    user = current_user
    
    summary_data = AnalyticsService.get_user_summary(db, user.id, period)
    analytics = AnalyticsService.save_analytics(db, user.id, summary_data, period)
    
    return {
        "id": analytics.id,
        "score": analytics.score,
        "summary": analytics.summary,
        "period": analytics.period,
        "created_at": analytics.created_at,
    }
