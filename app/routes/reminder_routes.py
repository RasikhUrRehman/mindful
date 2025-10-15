from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Reminder
from app.schemas.reminder_schema import ReminderCreate, ReminderUpdate, ReminderResponse, TimerRequest
from app.services.reminder_service import ReminderService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/reminders", tags=["reminders"])


# Use get_current_user dependency from app.core.security


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new reminder."""
    user = current_user
    
    reminder = ReminderService.create_reminder(
        db=db,
        user_id=user.id,
        reminder_type=reminder_data.reminder_type,
        title=reminder_data.title,
        message=reminder_data.message,
        trigger_time=reminder_data.trigger_time,
        frequency=reminder_data.frequency,
    )
    
    return reminder


@router.get("/", response_model=List[ReminderResponse])
def get_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all reminders for the current user."""
    reminders = db.query(Reminder).filter(Reminder.user_id == current_user.id).all()
    return reminders


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific reminder."""
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id,
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )
    
    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a reminder."""
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id,
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )
    
    update_data = reminder_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)
    
    db.commit()
    db.refresh(reminder)
    
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a reminder."""
    if not ReminderService.delete_reminder(db, reminder_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )


@router.post("/timer/start", status_code=status.HTTP_202_ACCEPTED)
def start_timer(
    timer_data: TimerRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start a timer that will trigger a notification after specified duration.
    
    - **timer_type**: meditation, exercise, mindful_eating, break, or custom
    - **duration_seconds**: Duration in seconds
    - **title**: Optional timer title
    """
    user = current_user
    
    # Create a reminder with trigger time
    trigger_time = datetime.utcnow()
    reminder = ReminderService.create_reminder(
        db=db,
        user_id=user.id,
        reminder_type=timer_data.timer_type,
        title=timer_data.title or f"{timer_data.timer_type.capitalize()} Timer",
        message=f"Your {timer_data.timer_type} timer of {timer_data.duration_seconds} seconds has completed!",
        trigger_time=trigger_time,
    )
    
    # Schedule background task to trigger notification
    async def trigger_notification():
        import asyncio
        await asyncio.sleep(timer_data.duration_seconds)
        
        # Update reminder status
        ReminderService.update_reminder_status(db, reminder.id, "triggered")
        
        # Send notification
        notification = NotificationService.create_notification(
            user_id=user.id,
            reminder_id=reminder.id,
            title=reminder.title,
            message=reminder.message,
        )
        NotificationService.send_notification(notification)
    
    background_tasks.add_task(trigger_notification)
    
    return {
        "message": "Timer started",
        "reminder_id": reminder.id,
        "duration_seconds": timer_data.duration_seconds,
    }


@router.get("/pending", response_model=List[ReminderResponse])
def get_pending_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all pending reminders that should be triggered."""
    reminders = ReminderService.get_pending_reminders(db, current_user.id)
    return reminders


@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
def mark_reminder_complete(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a reminder as completed."""
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id,
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )
    
    reminder = ReminderService.update_reminder_status(db, reminder_id, "completed")
    return reminder
