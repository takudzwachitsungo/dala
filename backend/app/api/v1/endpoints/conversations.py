"""Conversation endpoints - Placeholder for WebSocket integration"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.conversation import Conversation, Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    FeedbackCreate
)
from app.api.deps import get_current_user


router = APIRouter()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    
    conversation = Conversation(
        user_id=current_user.id,
        mode=data.mode,
        title=data.title
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        mode=conversation.mode.value,
        title=conversation.title,
        started_at=conversation.started_at,
        is_active=conversation.is_active,
        message_count=0
    )


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's conversations"""
    
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.started_at))
    )
    conversations = result.scalars().all()
    
    response = []
    for conv in conversations:
        # Get message count
        count_result = await db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conv.id)
        )
        message_count = count_result.scalar() or 0
        
        # Get last message
        last_msg_result = await db.execute(
            select(Message.content)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_message = last_msg_result.scalar_one_or_none()
        
        response.append(ConversationResponse(
            id=conv.id,
            mode=conv.mode.value,
            title=conv.title,
            started_at=conv.started_at,
            is_active=conv.is_active,
            message_count=message_count,
            last_message=last_message
        ))
    
    return response


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages from a conversation"""
    
    # Verify conversation belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role.value,
            content=msg.content,
            sentiment_score=msg.sentiment_score,
            emotion_tags=msg.emotion_tags or [],
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a conversation"""
    
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.is_active = False
    await db.commit()
    
    return None


@router.post("/{conversation_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    conversation_id: UUID,
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback for conversation quality (for fine-tuning dataset)"""
    
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Store feedback in metadata
    if not conversation.metadata:
        conversation.metadata = {}
    
    conversation.metadata["quality_score"] = feedback.quality_score
    if feedback.feedback_text:
        conversation.metadata["feedback_text"] = feedback.feedback_text
    
    await db.commit()
    
    # TODO: If quality_score >= 4, queue for training data export
    
    return None
