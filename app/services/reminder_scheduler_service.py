import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import Reminder, User
from app.services.fcm_service import FCMService

logger = logging.getLogger(__name__)


class ReminderSchedulerService:
    """Background service for checking and sending reminder notifications."""
    
    _scheduler: Optional[BackgroundScheduler] = None
    _running = False
    
    @classmethod
    def start(cls):
        """Start the reminder scheduler service."""
        if cls._running:
            logger.info("Reminder scheduler is already running")
            return
        
        try:
            # Initialize FCM
            FCMService.initialize()
            
            # Create scheduler
            cls._scheduler = BackgroundScheduler(timezone='UTC')
            
            # Add job to check reminders every minute
            cls._scheduler.add_job(
                func=cls._check_and_send_reminders,
                trigger=IntervalTrigger(minutes=1),
                id='check_reminders',
                name='Check and send due reminders',
                replace_existing=True
            )
            
            # Start scheduler
            cls._scheduler.start()
            cls._running = True
            logger.info("Reminder scheduler service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start reminder scheduler service: {str(e)}")
            raise
    
    @classmethod
    def stop(cls):
        """Stop the reminder scheduler service."""
        if cls._scheduler and cls._running:
            cls._scheduler.shutdown()
            cls._running = False
            logger.info("Reminder scheduler service stopped")
    
    @classmethod
    def _check_and_send_reminders(cls):
        """Check for due reminders and send notifications."""
        db: Session = SessionLocal()
        try:
            now = datetime.utcnow()
            
            # Query for pending reminders with active users that have FCM tokens
            # We get all pending reminders and filter by timezone-adjusted time
            pending_reminders = db.query(Reminder).join(User).filter(
                Reminder.status == "pending",
                Reminder.is_active == True,
                User.is_active == True,
                User.fcm_token.isnot(None)
            ).all()
            
            if not pending_reminders:
                logger.debug("No pending reminders found")
                return
            
            # Filter reminders that are due considering user's timezone
            due_reminders = []
            for reminder in pending_reminders:
                user = reminder.user
                
                # The reminder.trigger_time is stored as user's local time
                # We need to convert it to UTC for comparison with server time
                # using the user's GMT offset
                
                if user.gmt_offset_minutes is not None:
                    # Convert reminder trigger time from user's local time to UTC
                    # If user is GMT+5 (offset = 300 minutes), and reminder is at 14:00 local
                    # then UTC time should be 09:00 (14:00 - 5 hours)
                    reminder_utc_time = reminder.trigger_time - timedelta(minutes=user.gmt_offset_minutes)
                    
                    # Check if reminder is due (within the next minute window)
                    if reminder_utc_time <= now + timedelta(minutes=1) and reminder_utc_time > now - timedelta(minutes=2):
                        due_reminders.append(reminder)
                        logger.debug(f"Reminder {reminder.id} is due for user {user.id} (GMT offset: {user.gmt_offset_minutes} min)")
                else:
                    # No timezone info, assume trigger_time is already in UTC (backward compatibility)
                    if reminder.trigger_time <= now + timedelta(minutes=1) and reminder.trigger_time > now - timedelta(minutes=2):
                        due_reminders.append(reminder)
                        logger.debug(f"Reminder {reminder.id} is due for user {user.id} (no timezone info, using UTC)")
            
            if not due_reminders:
                logger.debug("No due reminders found after timezone filtering")
                return
            
            logger.info(f"Found {len(due_reminders)} due reminders to process")
            
            # Process each reminder
            for reminder in due_reminders:
                try:
                    cls._send_reminder_notification(db, reminder)
                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.id}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"Successfully processed {len(due_reminders)} reminders")
            
        except Exception as e:
            logger.error(f"Error checking reminders: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    @classmethod
    def _send_reminder_notification(cls, db: Session, reminder: Reminder):
        """
        Send notification for a specific reminder.
        
        Args:
            db: Database session
            reminder: Reminder object to process
        """
        user = reminder.user
        
        if not user.fcm_token:
            logger.warning(f"User {user.id} has no FCM token, skipping reminder {reminder.id}")
            reminder.status = "cancelled"
            reminder.updated_at = datetime.utcnow()
            return
        
        # Send FCM notification
        success = FCMService.send_reminder_notification(
            fcm_token=user.fcm_token,
            reminder_title=reminder.title,
            reminder_message=reminder.message,
            reminder_id=reminder.id,
            reminder_type=reminder.reminder_type
        )
        
        if success:
            logger.info(f"Successfully sent reminder {reminder.id} to user {user.id}")
            
            # Update reminder status based on frequency
            if reminder.frequency and reminder.frequency != "one-time":
                # For recurring reminders, schedule the next occurrence
                reminder.status = "triggered"
                cls._schedule_next_occurrence(reminder)
            else:
                # For one-time reminders, mark as completed
                reminder.status = "completed"
            
        else:
            logger.error(f"Failed to send reminder {reminder.id} to user {user.id}")
            reminder.status = "failed"
        
        reminder.updated_at = datetime.utcnow()
    
    @classmethod
    def _schedule_next_occurrence(cls, reminder: Reminder):
        """
        Schedule the next occurrence for a recurring reminder.
        
        Args:
            reminder: Reminder object to reschedule
        """
        if not reminder.frequency:
            return
        
        current_trigger = reminder.trigger_time
        
        # Calculate next trigger time based on frequency
        # The trigger time is stored in the user's local time
        if reminder.frequency == "daily":
            next_trigger = current_trigger + timedelta(days=1)
        elif reminder.frequency == "weekly":
            next_trigger = current_trigger + timedelta(weeks=1)
        elif reminder.frequency == "monthly":
            # Add approximately 30 days for monthly
            next_trigger = current_trigger + timedelta(days=30)
        elif reminder.frequency == "hourly":
            next_trigger = current_trigger + timedelta(hours=1)
        else:
            # Unknown frequency, don't reschedule
            logger.warning(f"Unknown frequency '{reminder.frequency}' for reminder {reminder.id}")
            return
        
        # Update trigger time and reset status to pending
        reminder.trigger_time = next_trigger
        reminder.status = "pending"
        
        logger.info(f"Rescheduled reminder {reminder.id} to {next_trigger} (user's local time)")
    
    @classmethod
    def is_running(cls) -> bool:
        """Check if scheduler is running."""
        return cls._running
