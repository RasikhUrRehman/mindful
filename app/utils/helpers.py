from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import Mood, Habit, Goal, Analytics
import base64
import re
import logging

logger = logging.getLogger(__name__)


def calculate_mood_average(moods: List[Mood]) -> Optional[str]:
    """Calculate average mood from a list of moods."""
    if not moods:
        return None
    
    mood_scores = {
        "excellent": 5,
        "good": 4,
        "neutral": 3,
        "sad": 1,
        "anxious": 2,
        "angry": 1,
    }
    
    total_score = sum(mood_scores.get(mood.mood_type, 0) for mood in moods)
    avg_score = total_score / len(moods)
    
    if avg_score >= 4.5:
        return "excellent"
    elif avg_score >= 3.5:
        return "good"
    elif avg_score >= 2.5:
        return "neutral"
    else:
        return "sad"


def calculate_habit_completion_rate(habits: List[Habit]) -> float:
    """Calculate habit completion rate."""
    if not habits:
        return 0.0
    
    total_rate = sum(habit.success_rate for habit in habits)
    return total_rate / len(habits)


def calculate_goal_progress(goals: List[Goal]) -> float:
    """Calculate overall goal progress."""
    if not goals:
        return 0.0
    
    total_progress = sum(goal.completion_percentage for goal in goals)
    return total_progress / len(goals)


def generate_insights(mood_avg: str, habit_rate: float, goal_progress: float) -> str:
    """Generate insights based on user data."""
    insights = []
    
    if mood_avg == "excellent":
        insights.append("Your mood has been excellent! Keep up the great work with your mindfulness practices.")
    elif mood_avg == "good":
        insights.append("Your mood is good overall. Continue with your current habits to maintain this positive state.")
    elif mood_avg == "neutral":
        insights.append("Your mood is neutral. Try increasing your daily mindfulness or physical activity.")
    else:
        insights.append("Your mood needs some attention. Consider adding more relaxation or meditation practices.")
    
    if habit_rate >= 0.8:
        insights.append(f"Excellent habit completion rate of {habit_rate*100:.1f}%! You're staying consistent.")
    elif habit_rate >= 0.5:
        insights.append(f"Good habit completion rate of {habit_rate*100:.1f}%. Try to be more consistent.")
    else:
        insights.append(f"Your habit completion is at {habit_rate*100:.1f}%. Start small and build momentum.")
    
    if goal_progress >= 0.8:
        insights.append("You're almost there with your goals! Keep pushing forward.")
    elif goal_progress >= 0.5:
        insights.append("You're making good progress on your goals. Stay focused and consistent.")
    else:
        insights.append("You're in the early stages of your goals. Break them down into smaller milestones.")
    
    return " ".join(insights)


def process_base64_image(image_data: Optional[str]) -> Optional[str]:
    """
    Process and validate Base64 image data.
    
    Args:
        image_data: Base64 encoded image string, optionally with data URI prefix
        
    Returns:
        Cleaned Base64 string without data URI prefix, or None if invalid
    """
    if not image_data:
        return None
    
    try:
        # Remove data URI prefix if present (e.g., "data:image/png;base64,")
        if image_data.startswith('data:'):
            # Extract just the base64 part
            match = re.match(r'data:image/[^;]+;base64,(.+)', image_data)
            if match:
                image_data = match.group(1)
            else:
                logger.warning("Invalid data URI format")
                return None
        
        # Remove any whitespace
        image_data = image_data.strip()
        
        # Validate Base64 encoding by attempting to decode
        try:
            base64.b64decode(image_data, validate=True)
        except Exception as e:
            logger.error(f"Invalid Base64 encoding: {e}")
            return None
        
        # Return the cleaned Base64 string (store with data URI for consistency)
        # This allows easy display in web/mobile apps
        return f"data:image/jpeg;base64,{image_data}"
        
    except Exception as e:
        logger.error(f"Error processing Base64 image: {e}")
        return None
