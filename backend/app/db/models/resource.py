"""Resource model for curated content"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from app.db.base import Base


class Resource(Base):
    """Curated mental health resource"""
    
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    resource_type = Column(String(50), nullable=False)  # music, reading, exercise, video, article
    category = Column(String(50), nullable=False)  # anxiety, grief, burnout, relaxation, etc.
    
    url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Content metadata
    duration_minutes = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    tags = Column(ARRAY(String), default=[], nullable=False)
    
    # Engagement
    view_count = Column(Integer, default=0, nullable=False)
    helpful_count = Column(Integer, default=0, nullable=False)
    
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Resource {self.title}>"
