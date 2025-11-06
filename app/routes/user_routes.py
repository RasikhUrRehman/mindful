from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_password, hash_password
from app.models.user import User
from app.schemas.user_schema import (
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    FCMTokenUpdate,
    FCMTokenResponse,
)
from app.schemas.analytics_schema import ProgressResponse
from app.services.analytics_service import AnalyticsService
from app.utils.helpers import process_base64_image
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


# Use get_current_user dependency from app.core.security


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's profile."""
    return current_user


@router.put("/profile")
def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile with Base64 image support."""
    try:
        user = current_user
        update_data = profile_data.dict(exclude_unset=True)
        
        logger.info(f"Updating user {user.id} profile")
        
        # Process Base64 image if present
        if 'picture' in update_data and update_data['picture']:
            processed_image = process_base64_image(update_data['picture'])
            if processed_image is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format. Please provide a valid Base64 encoded image."
                )
            update_data['picture'] = processed_image
        
        # Update user fields
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return {"success": True, "message": "Profile updated successfully", "user": user}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the profile"
        )


@router.get("/profile/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get a user's profile (public information)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.post("/change-password", response_model=ChangePasswordResponse)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password."""
    user = current_user
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Update password
    user.password_hash = hash_password(password_data.new_password)
    db.commit()
    
    return ChangePasswordResponse(message="Password changed successfully")


@router.post("/fcm-token", response_model=FCMTokenResponse)
def register_fcm_token(
    token_data: FCMTokenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register or update FCM token for push notifications."""
    try:
        user = current_user
        user.fcm_token = token_data.fcm_token
        
        # Calculate GMT offset if device timestamp is provided
        if token_data.device_timestamp:
            try:
                from datetime import datetime
                # Parse device timestamp (ISO format)
                device_time = datetime.fromisoformat(token_data.device_timestamp.replace('Z', '+00:00'))
                server_time = datetime.utcnow()
                
                # Calculate offset in minutes
                # device_time is the user's local time, server_time is UTC
                # If device is ahead of UTC, offset is positive
                time_diff = device_time.replace(tzinfo=None) - server_time
                gmt_offset_minutes = int(time_diff.total_seconds() / 60)
                
                user.gmt_offset_minutes = gmt_offset_minutes
                logger.info(f"Calculated GMT offset for user {user.id}: {gmt_offset_minutes} minutes")
                
            except Exception as e:
                logger.warning(f"Failed to calculate GMT offset for user {user.id}: {e}")
                # Continue without setting GMT offset
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"FCM token updated for user {user.id}")
        
        return FCMTokenResponse(
            success=True,
            message="FCM token registered successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating FCM token for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register FCM token"
        )


@router.delete("/fcm-token", response_model=FCMTokenResponse)
def unregister_fcm_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unregister FCM token (e.g., on logout)."""
    try:
        user = current_user
        user.fcm_token = None
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"FCM token removed for user {user.id}")
        
        return FCMTokenResponse(
            success=True,
            message="FCM token unregistered successfully"
        )
        
    except Exception as e:
        logger.error(f"Error removing FCM token for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unregister FCM token"
        )
