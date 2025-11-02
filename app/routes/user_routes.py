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
