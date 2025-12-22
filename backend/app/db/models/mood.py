"""Mood tracking model"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class MoodEntry(Base):
    """Mood entry model"""
    
    __tablename__ = "mood_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Mood score (1-10 scale matching frontend)
    mood_score = Column(Integer, nullable=False)
    
    # Emotions and activities
    emotions = Column(ARRAY(Text), default=[], nullable=True)
    activities = Column(ARRAY(Text), default=[], nullable=True)
    
    # Optional notes
    notes = Column(Text, nullable=True)
    
    # Optional link to conversation
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="mood_entries")
    
    def __repr__(self):
        return f"<MoodEntry {self.id} score={self.mood_score}>"
