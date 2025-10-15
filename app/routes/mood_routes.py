from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Mood
from app.schemas.mood_schema import MoodCreate, MoodUpdate, MoodResponse, MoodSummary

router = APIRouter(prefix="/moods", tags=["moods"])





@router.post("/", response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
def create_mood(
    mood_data: MoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new mood entry."""
    user = current_user
    
    mood = Mood(
        user_id=user.id,
        mood_type=mood_data.mood_type,
        intensity=mood_data.intensity,
        note=mood_data.note,
        timestamp=datetime.utcnow(),
    )
    
    db.add(mood)
    db.commit()
    db.refresh(mood)
    
    return mood


@router.get("/", response_model=List[MoodResponse])
def get_moods(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all mood entries for the current user."""
    moods = db.query(Mood).filter(Mood.user_id == current_user.id).order_by(Mood.timestamp.desc()).all()
    return moods


@router.get("/{mood_id}", response_model=MoodResponse)
def get_mood(mood_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific mood entry."""
    mood = db.query(Mood).filter(
        Mood.id == mood_id,
        Mood.user_id == current_user.id,
    ).first()
    
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found",
        )
    
    return mood


@router.put("/{mood_id}", response_model=MoodResponse)
def update_mood(
    mood_id: int,
    mood_data: MoodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a mood entry."""
    mood = db.query(Mood).filter(
        Mood.id == mood_id,
        Mood.user_id == current_user.id,
    ).first()
    
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found",
        )
    
    update_data = mood_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mood, field, value)
    
    db.commit()
    db.refresh(mood)
    
    return mood


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood(mood_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a mood entry."""
    mood = db.query(Mood).filter(
        Mood.id == mood_id,
        Mood.user_id == current_user.id,
    ).first()
    
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found",
        )
    
    db.delete(mood)
    db.commit()


@router.get("/summary/weekly", response_model=MoodSummary)
def get_weekly_mood_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get weekly mood summary."""
    user = current_user
    
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=7)
    
    moods = db.query(Mood).filter(
        Mood.user_id == user.id,
        Mood.created_at >= start_date,
    ).all()
    
    if not moods:
        return MoodSummary(
            period="weekly",
            average_mood="neutral",
            average_intensity=None,
            most_common_mood="none",
            total_entries=0,
            mood_breakdown={},
        )
    
    mood_breakdown = {}
    total_intensity = 0
    count_with_intensity = 0
    
    for mood in moods:
        mood_breakdown[mood.mood_type] = mood_breakdown.get(mood.mood_type, 0) + 1
        if mood.intensity:
            total_intensity += mood.intensity
            count_with_intensity += 1
    
    most_common = max(mood_breakdown, key=mood_breakdown.get)
    average_intensity = total_intensity / count_with_intensity if count_with_intensity > 0 else None
    
    mood_scores = {
        "excellent": 5,
        "good": 4,
        "neutral": 3,
        "sad": 1,
        "anxious": 2,
        "angry": 1,
    }
    
    avg_score = sum(mood_scores.get(m.mood_type, 0) for m in moods) / len(moods)
    if avg_score >= 4:
        avg_mood = "excellent"
    elif avg_score >= 3:
        avg_mood = "good"
    elif avg_score >= 2:
        avg_mood = "neutral"
    else:
        avg_mood = "sad"
    
    return MoodSummary(
        period="weekly",
        average_mood=avg_mood,
        average_intensity=average_intensity,
        most_common_mood=most_common,
        total_entries=len(moods),
        mood_breakdown=mood_breakdown,
    )
