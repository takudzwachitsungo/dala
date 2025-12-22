"""Conversation schemas"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ConversationCreate(BaseModel):
    """Create conversation schema"""
    mode: str = Field(..., pattern="^(listen|reflect|ground)$")
    title: Optional[str] = None


class MessageCreate(BaseModel):
    """Create message schema"""
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Message response schema"""
    id: UUID
    role: str
    content: str
    sentiment_score: Optional[float] = None
    emotion_tags: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: UUID
    mode: str
    title: Optional[str] = None
    started_at: datetime
    is_active: bool
    message_count: Optional[int] = None
    last_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Detailed conversation with messages"""
    messages: List[MessageResponse] = []


class FeedbackCreate(BaseModel):
    """Feedback for conversation quality"""
    quality_score: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
