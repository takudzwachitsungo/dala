"""User milestone model"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class UserMilestone(Base):
    """User milestone/badge model"""
    
    __tablename__ = "user_milestones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Milestone type (first_checkin, week_streak, ten_conversations, etc.)
    milestone_type = Column(String(100), nullable=False)
    
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="milestones")
    
    def __repr__(self):
        return f"<UserMilestone {self.milestone_type}>"
