from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.models.user import Mood, Habit, Goal, Analytics
from app.utils.helpers import (
    calculate_mood_average,
    calculate_habit_completion_rate,
    calculate_goal_progress,
    generate_insights,
)


class AnalyticsService:
    """Service for generating analytics and insights."""
    
    @staticmethod
    def get_user_summary(db: Session, user_id: int, period: str = "weekly") -> dict:
        """
        Get user summary for a specific period.
        
        Args:
            db: Database session
            user_id: User ID
            period: 'daily', 'weekly', or 'monthly'
        """
        # Calculate time range
        now = datetime.utcnow()
        if period == "daily":
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=7)
        
        # Get moods for period
        moods = db.query(Mood).filter(
            and_(
                Mood.user_id == user_id,
                Mood.created_at >= start_date,
                Mood.created_at <= now,
            )
        ).all()
        
        # Get habits
        habits = db.query(Habit).filter(
            Habit.user_id == user_id,
            Habit.is_active == True,
        ).all()
        
        # Get goals
        goals = db.query(Goal).filter(
            Habit.user_id == user_id,
        ).all()
        
        # Calculate metrics
        mood_avg = calculate_mood_average(moods)
        habit_rate = calculate_habit_completion_rate(habits)
        goal_progress = calculate_goal_progress(goals)
        
        # Calculate overall score (0-100)
        mood_score = {"excellent": 100, "good": 80, "neutral": 60, "sad": 40}.get(mood_avg, 50)
        overall_score = (mood_score + habit_rate * 100 + goal_progress) / 3
        
        # Generate insights
        insights = generate_insights(mood_avg or "neutral", habit_rate, goal_progress)
        
        return {
            "overall_score": round(overall_score, 2),
            "mood_average": mood_avg,
            "habit_completion_rate": round(habit_rate, 2),
            "goal_progress": round(goal_progress, 2),
            "mood_count": len(moods),
            "habit_count": len(habits),
            "goal_count": len(goals),
            "insights": insights,
            "period": period,
        }
    
    @staticmethod
    def get_mood_breakdown(db: Session, user_id: int, days: int = 7) -> dict:
        """Get mood breakdown for the last N days."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        moods = db.query(Mood).filter(
            and_(
                Mood.user_id == user_id,
                Mood.created_at >= start_date,
            )
        ).all()
        
        mood_breakdown = {}
        for mood in moods:
            mood_breakdown[mood.mood_type] = mood_breakdown.get(mood.mood_type, 0) + 1
        
        return mood_breakdown
    
    @staticmethod
    def get_habit_stats(db: Session, user_id: int) -> dict:
        """Get habit statistics."""
        habits = db.query(Habit).filter(Habit.user_id == user_id).all()
        
        if not habits:
            return {"total": 0, "active": 0, "avg_streak": 0, "avg_success_rate": 0}
        
        active_habits = [h for h in habits if h.is_active]
        avg_streak = sum(h.streak_count for h in habits) / len(habits)
        avg_success_rate = sum(h.success_rate for h in habits) / len(habits)
        
        return {
            "total": len(habits),
            "active": len(active_habits),
            "avg_streak": round(avg_streak, 2),
            "avg_success_rate": round(avg_success_rate, 2),
        }
    
    @staticmethod
    def save_analytics(
        db: Session,
        user_id: int,
        summary_data: dict,
        period: str = "weekly",
    ) -> Analytics:
        """Save analytics record to database."""
        analytics = Analytics(
            user_id=user_id,
            summary=summary_data["insights"],
            score=summary_data["overall_score"],
            mood_average=summary_data["mood_average"],
            habit_completion_rate=summary_data["habit_completion_rate"],
            goal_progress=summary_data["goal_progress"],
            insights=str(summary_data),
            period=period,
        )
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics
