"""Guided Path models for structured mental health journeys"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Path(Base):
    """Guided mental health path"""
    
    __tablename__ = "paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # anxiety, grief, burnout, etc.
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)  # For UI theming
    
    difficulty = Column(String(20), default="beginner", nullable=False)  # beginner, intermediate, advanced
    estimated_duration = Column(Integer, nullable=True)  # In days
    step_count = Column(Integer, default=0, nullable=False)
    
    is_published = Column(Boolean, default=True, nullable=False)
    enrollment_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    steps = relationship("PathStep", back_populates="path", cascade="all, delete-orphan", order_by="PathStep.order_index")
    user_progress = relationship("UserPathProgress", back_populates="path", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Path {self.name}>"


class PathStep(Base):
    """Individual step in a guided path"""
    
    __tablename__ = "path_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_id = Column(UUID(as_uuid=True), ForeignKey("paths.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    content = Column(Text, nullable=False)  # Main content/instructions
    
    order_index = Column(Integer, nullable=False)
    step_type = Column(String(50), default="reflection", nullable=False)  # reflection, exercise, reading, etc.
    
    # Exercise/reflection prompts
    prompts = Column(JSONB, default=[], nullable=False)  # List of reflection questions
    resources = Column(JSONB, default=[], nullable=False)  # List of related resources
    
    estimated_minutes = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    path = relationship("Path", back_populates="steps")
    
    def __repr__(self):
        return f"<PathStep {self.title}>"


class UserPathProgress(Base):
    """User's progress through a guided path"""
    
    __tablename__ = "user_path_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    path_id = Column(UUID(as_uuid=True), ForeignKey("paths.id", ondelete="CASCADE"), nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    current_step_index = Column(Integer, default=0, nullable=False)
    completed_steps = Column(JSONB, default=[], nullable=False)  # List of completed step IDs
    reflection_logs = Column(JSONB, default={}, nullable=False)  # step_id -> reflection text
    
    progress_percentage = Column(Float, default=0.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", backref="path_progress")
    path = relationship("Path", back_populates="user_progress")
    
    def __repr__(self):
        return f"<UserPathProgress user={self.user_id} path={self.path_id} progress={self.progress_percentage}%>"
