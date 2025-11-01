from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, PersonalInspiration
from app.schemas.personal_inspiration_schema import (
    PersonalInspirationCreate,
    PersonalInspirationUpdate,
    PersonalInspirationResponse,
)

router = APIRouter(prefix="/inspirations", tags=["inspirations"])


@router.post("/", response_model=PersonalInspirationResponse, status_code=status.HTTP_201_CREATED)
def create_inspiration(
    inspiration_data: PersonalInspirationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new personal inspiration."""
    user = current_user
    
    inspiration = PersonalInspiration(
        user_id=user.id,
        inspiration=inspiration_data.inspiration,
    )
    
    db.add(inspiration)
    db.commit()
    db.refresh(inspiration)
    
    return inspiration


@router.get("/", response_model=List[PersonalInspirationResponse])
def get_inspirations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all personal inspirations for the current user."""
    inspirations = db.query(PersonalInspiration).filter(
        PersonalInspiration.user_id == current_user.id
    ).order_by(PersonalInspiration.created_at.desc()).all()
    return inspirations


@router.get("/{inspiration_id}", response_model=PersonalInspirationResponse)
def get_inspiration(
    inspiration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific personal inspiration."""
    inspiration = db.query(PersonalInspiration).filter(
        PersonalInspiration.id == inspiration_id,
        PersonalInspiration.user_id == current_user.id,
    ).first()
    
    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspiration not found",
        )
    
    return inspiration


@router.put("/{inspiration_id}", response_model=PersonalInspirationResponse)
def update_inspiration(
    inspiration_id: int,
    inspiration_data: PersonalInspirationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a personal inspiration."""
    inspiration = db.query(PersonalInspiration).filter(
        PersonalInspiration.id == inspiration_id,
        PersonalInspiration.user_id == current_user.id,
    ).first()
    
    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspiration not found",
        )
    
    update_data = inspiration_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inspiration, field, value)
    
    db.commit()
    db.refresh(inspiration)
    
    return inspiration


@router.delete("/{inspiration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspiration(
    inspiration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a personal inspiration."""
    inspiration = db.query(PersonalInspiration).filter(
        PersonalInspiration.id == inspiration_id,
        PersonalInspiration.user_id == current_user.id,
    ).first()
    
    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspiration not found",
        )
    
    db.delete(inspiration)
    db.commit()
    
    return None
