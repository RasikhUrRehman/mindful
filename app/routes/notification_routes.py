from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.fcm_service import FCMService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class TestNotificationRequest(BaseModel):
    """Schema for test notification request."""
    title: str
    message: str


class NotificationStatusResponse(BaseModel):
    """Schema for notification status response."""
    fcm_initialized: bool
    scheduler_running: bool
    user_has_token: bool
    message: str


@router.post("/test")
def send_test_notification(
    notification: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a test notification to the current user.
    Useful for testing FCM setup.
    """
    try:
        if not current_user.fcm_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No FCM token registered. Please register your device token first."
            )
        
        # Send test notification
        success = FCMService.send_notification(
            fcm_token=current_user.fcm_token,
            title=notification.title,
            body=notification.message,
            data={
                "notification_type": "test",
                "user_id": str(current_user.id)
            }
        )
        
        if success:
            return {
                "success": True,
                "message": "Test notification sent successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test notification. Check server logs for details."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test notification to user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending test notification: {str(e)}"
        )


@router.get("/status", response_model=NotificationStatusResponse)
def get_notification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the status of the notification system for the current user.
    """
    from app.services.reminder_scheduler_service import ReminderSchedulerService
    
    fcm_initialized = FCMService._initialized
    scheduler_running = ReminderSchedulerService.is_running()
    user_has_token = current_user.fcm_token is not None
    
    messages = []
    if not fcm_initialized:
        messages.append("FCM not initialized - check Firebase credentials")
    if not scheduler_running:
        messages.append("Reminder scheduler is not running")
    if not user_has_token:
        messages.append("No FCM token registered for this user")
    
    if not messages:
        messages.append("All systems operational")
    
    return NotificationStatusResponse(
        fcm_initialized=fcm_initialized,
        scheduler_running=scheduler_running,
        user_has_token=user_has_token,
        message="; ".join(messages)
    )
