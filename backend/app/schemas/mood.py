"""Mood schemas"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class MoodEntryCreate(BaseModel):
    """Create mood entry schema"""
    mood_score: int = Field(..., ge=1, le=10, description="Mood score 1-10")
    emotions: Optional[List[str]] = Field(default_factory=list)
    activities: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)
    conversation_id: Optional[UUID] = None


class MoodEntryResponse(BaseModel):
    """Mood entry response schema"""
    id: UUID
    mood_score: int
    emotions: List[str]
    activities: List[str]
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MoodHistoryResponse(BaseModel):
    """Mood history aggregated data"""
    entries: List[MoodEntryResponse]
    average_score: float
    trend: str  # "improving", "declining", "stable"
    total_entries: int
