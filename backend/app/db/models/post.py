"""Post and Reaction models for community circles"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.base import Base


class Post(Base):
    """Community post model"""
    
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    circle_id = Column(UUID(as_uuid=True), ForeignKey("circles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)  # For replies
    
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    
    # Engagement metrics
    reaction_count = Column(Integer, default=0, nullable=False)
    reply_count = Column(Integer, default=0, nullable=False)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    flag_reason = Column(String(255), nullable=True)
    
    # Phase 3: Enhanced moderation
    flag_severity = Column(String(20), nullable=True)  # low, medium, high, critical
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    circle = relationship("Circle", back_populates="posts")
    user = relationship("User", foreign_keys=[user_id], backref="posts")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    parent = relationship("Post", remote_side=[id], backref="replies")
    reactions = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post {self.id} in circle={self.circle_id}>"


class PostReaction(Base):
    """Reaction to a post (e.g., 'I relate')"""
    
    __tablename__ = "post_reactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    reaction_type = Column(String(20), default="relate", nullable=False)  # relate, support, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="reactions")
    user = relationship("User", backref="post_reactions")
    
    def __repr__(self):
        return f"<PostReaction {self.reaction_type} on post={self.post_id}>"
