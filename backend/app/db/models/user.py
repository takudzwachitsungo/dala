"""User model"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for anonymous users
    
    # User flags
    is_anonymous = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Phase 3: Roles and permissions
    role = Column(String(20), default='user', nullable=False)  # user, moderator, admin
    is_moderator = Column(Boolean, default=False, nullable=False)
    is_peer_supporter = Column(Boolean, default=False, nullable=False)
    moderation_notes = Column(Text, nullable=True)
    
    # Phase 3: Risk tracking
    risk_level = Column(String(20), default='low', nullable=False)  # low, medium, high, critical
    last_risk_assessment = Column(DateTime, nullable=True)
    escalation_status = Column(String(20), nullable=True)  # None, pending, escalated, resolved
    
    # Privacy
    privacy_consent = Column(Boolean, default=False, nullable=False)
    privacy_consent_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    milestones = relationship("UserMilestone", back_populates="user", cascade="all, delete-orphan")
    safety_plan = relationship("SafetyPlan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username} (anonymous={self.is_anonymous})>"
