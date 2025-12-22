from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


class PathStepBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    step_type: str = Field(default="reflection", pattern="^(reflection|exercise|education|practice)$")
    estimated_minutes: Optional[int] = None


class PathStepResponse(PathStepBase):
    id: int
    path_id: int
    order_index: int
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class PathBase(BaseModel):
    name: str = Field(..., max_length=200)
    category: str = Field(..., pattern="^(anxiety|grief|burnout|depression|relationships|growth)$")
    difficulty: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    estimated_duration: Optional[int] = None  # In days


class PathResponse(PathBase):
    id: UUID
    step_count: int = 0
    enrollment_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPathProgressResponse(BaseModel):
    id: UUID
    path_id: UUID
    current_step_index: int = 0
    progress_percentage: float = 0.0
    is_completed: bool = False
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_activity: datetime
    
    class Config:
        from_attributes = True


class PathDetailResponse(PathResponse):
    steps: List[PathStepResponse] = []
    user_progress: Optional[UserPathProgressResponse] = None


class PathProgressUpdate(BaseModel):
    current_step_index: int = Field(..., ge=0)
    completed_steps: Optional[Dict[str, Any]] = None


class StepReflectionCreate(BaseModel):
    step_id: int
    reflection: str = Field(..., min_length=1, max_length=2000)
    mood_rating: Optional[int] = Field(None, ge=1, le=10)
