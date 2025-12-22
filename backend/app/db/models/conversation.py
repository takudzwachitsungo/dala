"""Conversation and Message models"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.base import Base


class ConversationMode(str, enum.Enum):
    """Conversation mode enum"""
    LISTEN = "listen"
    REFLECT = "reflect"
    GROUND = "ground"


class MessageRole(str, enum.Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    """Conversation model"""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=True)
    mode = Column(
        Enum(ConversationMode, native_enum=False),
        nullable=False,
        default=ConversationMode.LISTEN
    )
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Cached conversation state (preferences, themes, etc.)
    conversation_metadata = Column(JSONB, default={}, nullable=False)
    
    summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id} mode={self.mode.value}>"


class Message(Base):
    """Message model"""
    
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    role = Column(
        Enum(MessageRole, native_enum=False),
        nullable=False
    )
    content = Column(Text, nullable=False)
    
    # Sentiment analysis
    sentiment_score = Column(Float, nullable=True)
    emotion_tags = Column(ARRAY(String), default=[], nullable=True)
    
    # Phase 3: Risk detection
    risk_score = Column(Float, nullable=True)
    risk_indicators = Column(JSONB, nullable=True)
    requires_escalation = Column(Boolean, default=False, nullable=False)
    
    # Additional context
    message_metadata = Column(JSONB, default={}, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id} role={self.role.value}>"
