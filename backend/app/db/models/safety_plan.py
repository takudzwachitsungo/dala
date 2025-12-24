"""Safety plan model"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid


class SafetyPlan(Base):
    """User's personal safety plan"""
    __tablename__ = "safety_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Warning signs
    warning_signs = Column(ARRAY(String), default=list)
    
    # Internal coping strategies (things I can do on my own)
    internal_coping = Column(ARRAY(String), default=list)
    
    # People who can help distract me
    social_contacts = Column(ARRAY(String), default=list)
    
    # People I can ask for help
    people_to_ask = Column(ARRAY(String), default=list)
    
    # Professional contacts
    professionals = Column(ARRAY(String), default=list)
    
    # Emergency contacts
    emergency_contacts = Column(ARRAY(String), default=list)
    
    # Making the environment safe
    safe_environment = Column(Text)
    
    # Reasons for living
    reasons_to_live = Column(ARRAY(String), default=list)
    
    # Relationship
    user = relationship("User", back_populates="safety_plan")
