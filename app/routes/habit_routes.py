from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Habit
from app.schemas.habit_schema import HabitCreate, HabitUpdate, HabitResponse

router = APIRouter(prefix="/habits", tags=["habits"])



@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new habit for the current user."""
    user = current_user
    
    habit = Habit(
        user_id=user.id,
        title=habit_data.title,
        category=habit_data.category,
        frequency=habit_data.frequency,
        description=habit_data.description,
    )
    
    db.add(habit)
    db.commit()
    db.refresh(habit)
    
    return habit


@router.get("/", response_model=List[HabitResponse])
def get_habits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all habits for the current user."""
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return habits


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific habit."""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id,
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    
    return habit


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a habit."""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id,
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    
    # Update fields
    update_data = habit_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a habit."""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id,
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    
    db.delete(habit)
    db.commit()


@router.post("/{habit_id}/complete", response_model=HabitResponse)
def mark_habit_complete(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a habit as completed for today."""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id,
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    
    # Increment streak and update success rate
    habit.streak_count += 1
    habit.success_rate = min(100.0, habit.success_rate + 5.0)
    
    db.commit()
    db.refresh(habit)
    
    return habit
