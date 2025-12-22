"""Circle (community group) models"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Circle(Base):
    """Circle (community group) model"""
    
    __tablename__ = "circles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    topic = Column(String(50), nullable=False)  # anxiety, grief, burnout, etc.
    icon = Column(String(50), nullable=True)  # emoji or icon identifier
    
    is_active = Column(Boolean, default=True, nullable=False)
    member_count = Column(Integer, default=0, nullable=False)
    post_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    memberships = relationship("CircleMembership", back_populates="circle", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="circle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Circle {self.name}>"


class CircleMembership(Base):
    """User membership in a circle"""
    
    __tablename__ = "circle_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    circle_id = Column(UUID(as_uuid=True), ForeignKey("circles.id", ondelete="CASCADE"), nullable=False)
    
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_moderator = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", backref="circle_memberships")
    circle = relationship("Circle", back_populates="memberships")
    
    def __repr__(self):
        return f"<CircleMembership user={self.user_id} circle={self.circle_id}>"
