from datetime import datetime, timedelta
from typing import Callable, Optional
from sqlalchemy.orm import Session
from app.models.user import Reminder
import asyncio


class ReminderService:
    """Service for managing reminders and timers."""
    
    @staticmethod
    def create_reminder(
        db: Session,
        user_id: int,
        reminder_type: str,
        title: str,
        message: str,
        trigger_time: datetime,
        frequency: Optional[str] = None,
    ) -> Reminder:
        """Create a new reminder."""
        reminder = Reminder(
            user_id=user_id,
            reminder_type=reminder_type,
            title=title,
            message=message,
            trigger_time=trigger_time,
            frequency=frequency,
            status="pending",
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder
    
    @staticmethod
    def update_reminder_status(
        db: Session,
        reminder_id: int,
        status: str,
    ) -> Optional[Reminder]:
        """Update reminder status."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if reminder:
            reminder.status = status
            reminder.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(reminder)
        return reminder
    
    @staticmethod
    def get_pending_reminders(db: Session, user_id: int) -> list:
        """Get all pending reminders for a user."""
        now = datetime.utcnow()
        reminders = db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.status == "pending",
            Reminder.trigger_time <= now,
            Reminder.is_active == True,
        ).all()
        return reminders
    
    @staticmethod
    async def schedule_timer(
        duration_seconds: int,
        callback: Optional[Callable] = None,
        callback_args: dict = None,
    ) -> None:
        """
        Schedule a timer that triggers a callback after specified duration.
        
        Args:
            duration_seconds: Timer duration in seconds
            callback: Optional callback function to execute
            callback_args: Arguments to pass to callback
        """
        await asyncio.sleep(duration_seconds)
        
        if callback and callable(callback):
            if callback_args:
                callback(**callback_args)
            else:
                callback()
    
    @staticmethod
    def delete_reminder(db: Session, reminder_id: int) -> bool:
        """Delete a reminder."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if reminder:
            db.delete(reminder)
            db.commit()
            return True
        return False
