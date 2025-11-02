from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

#   {
#     "assessment_name": "mindset & psychology",
#     "assessment_type": "MCQ",
#     "questions": {
#       "1": ["1"],
#       "2": ["1"],
#       "3": ["1"],
#       "4": ["1"],
#       "5": ["1"]
#     },
#     "results": {
#       "thinking_patterns": {
#         "1": "1/5",
#         "2": "1/5",
#         "3": "1/5"
#       },
#       "recommended_practices": "some text"
#     },
#     "id": 1,
#     "user_id": 1,
#     "created_at": "2025-11-01T23:27:15.131673",
#     "updated_at": "2025-11-01T23:27:15.131677"
#   }


class AssessmentBase(BaseModel):
    """Base assessment schema."""
    assessment_name: str = Field(..., min_length=1, max_length=255)
    assessment_type: str = Field(..., min_length=1, max_length=100)
    questions: Dict[str, List[str]] = Field(..., description="Questions with answers as list of strings: {\"1\": [\"answer1\"], \"2\": [\"answer2a\", \"answer2b\"]}")
    results: Dict[str, Any] = Field(..., description="Assessment results as JSON")


class AssessmentCreate(AssessmentBase):
    """Schema for creating a new assessment."""
    pass


class AssessmentUpdate(BaseModel):
    """Schema for updating an assessment."""
    assessment_name: Optional[str] = Field(None, min_length=1, max_length=255)
    assessment_type: Optional[str] = Field(None, min_length=1, max_length=100)
    questions: Optional[Dict[str, List[str]]] = None
    results: Optional[Dict[str, Any]] = None


class AssessmentResponse(AssessmentBase):
    """Schema for assessment responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
