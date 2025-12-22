"""Profile schemas"""

from typing import List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class MilestoneResponse(BaseModel):
    """Milestone response schema"""
    id: UUID
    milestone_type: str
    earned_at: datetime
    
    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    """User profile response"""
    id: UUID
    username: str
    created_at: datetime
    streak_days: int
    total_mood_entries: int
    total_conversations: int
    milestone_count: int
    milestones: List[MilestoneResponse] = []
    is_admin: bool = False
    is_anonymous: bool = False
    role: str = 'user'
    
    class Config:
        from_attributes = True
