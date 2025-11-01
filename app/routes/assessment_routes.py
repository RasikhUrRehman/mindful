from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Assessment
from app.schemas.assessment_schema import AssessmentCreate, AssessmentUpdate, AssessmentResponse

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new assessment."""
    user = current_user
    
    assessment = Assessment(
        user_id=user.id,
        assessment_name=assessment_data.assessment_name,
        assessment_type=assessment_data.assessment_type,
        questions=assessment_data.questions,
        results=assessment_data.results,
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return assessment


@router.get("/", response_model=List[AssessmentResponse])
def get_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all assessments for the current user."""
    assessments = db.query(Assessment).filter(Assessment.user_id == current_user.id).all()
    return assessments


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific assessment."""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    
    return assessment


@router.put("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: int,
    assessment_data: AssessmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an assessment."""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    
    update_data = assessment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)
    
    db.commit()
    db.refresh(assessment)
    
    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an assessment."""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    
    db.delete(assessment)
    db.commit()
    
    return None
