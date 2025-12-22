"""Conversation service orchestrating LangGraph, LLM, and database operations"""

from typing import AsyncGenerator, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from loguru import logger
import uuid

from app.db.models.conversation import Conversation, Message, MessageRole
from app.db.models.user import User
from app.db.models.mood import MoodEntry
from app.services.ai.conversation_graph import DalaConversationGraph, ConversationState
from app.services.cache_service import CacheService
from app.core.risk_detection import RiskDetector


class ConversationService:
    """Service for managing conversations with AI"""
    
    def __init__(self, cache_service: CacheService = None):
        self.graph = DalaConversationGraph()
        self.cache_service = cache_service
    
    async def stream_conversation(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        message: str,
        mode: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream AI response using LangGraph workflow
        
        Args:
            db: Database session
            user_id: User ID
            conversation_id: Conversation ID
            message: User's message
            mode: Conversation mode (listen, reflect, ground)
            
        Yields:
            Dict with type, content, and metadata
        """
        try:
            # Get user for context
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one()
            
            # Load cached context
            cached_context = {}
            if self.cache_service:
                cached_context = await self.cache_service.get_conversation_context(
                    str(conversation_id)
                ) or {}
            
            # If no cached context, build from database and mood history
            if not cached_context:
                cached_context = await self._build_context(db, user_id, conversation_id)
            
            # Add username to context
            cached_context["user_name"] = user.nickname or "friend"
            
            # Get recent messages for context
            result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .limit(5)
            )
            recent_messages = result.scalars().all()
            
            # Build message history
            messages = []
            for msg in reversed(recent_messages):
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            # Prepare conversation state
            state: ConversationState = {
                "messages": messages,
                "mode": mode,
                "user_id": str(user_id),
                "conversation_id": str(conversation_id),
                "cached_context": cached_context,
                "sentiment_score": 0.0,
                "primary_emotion": "neutral",
                "crisis_level": "NONE",
                "needs_crisis_support": False,
                "next_action": ""
            }
            
            # Run through LangGraph
            result_state = await self.graph.run_conversation(message, state)
            
            # Get AI response (last message in state)
            ai_response = result_state["messages"][-1]["content"]
            
            # Stream the response in chunks for real-time feel
            words = ai_response.split()
            chunk_size = 5
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size]) + " "
                yield {
                    "type": "chunk",
                    "content": chunk,
                    "done": False
                }
            
            # Send completion with metadata
            yield {
                "type": "complete",
                "content": "",
                "done": True,
                "metadata": {
                    "sentiment_score": result_state["sentiment_score"],
                    "primary_emotion": result_state["primary_emotion"],
                    "crisis_level": result_state["crisis_level"]
                }
            }
            
            # Save messages to database
            await self._save_messages(
                db,
                conversation_id,
                message,
                ai_response,
                result_state
            )
            
            # Update cached context
            if self.cache_service:
                updated_context = await self._build_context(db, user_id, conversation_id)
                await self.cache_service.cache_conversation_context(
                    str(conversation_id),
                    updated_context
                )
            
        except Exception as e:
            logger.error(f"Conversation streaming failed: {e}")
            yield {
                "type": "error",
                "content": "I'm having trouble connecting right now. Please try again.",
                "done": True,
                "error": str(e)
            }
    
    async def _build_context(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Build conversation context from database and memory cache"""
        
        # Get mood trend
        cutoff = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(func.avg(MoodEntry.mood_score))
            .where(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= cutoff
            )
        )
        avg_mood = result.scalar() or 5.0
        
        # Determine trend
        if avg_mood >= 7:
            mood_trend = "positive"
        elif avg_mood >= 4:
            mood_trend = "stable"
        else:
            mood_trend = "challenging"
        
        # Get conversation memory if cache service available
        conversation_memory = {}
        user_summary = {}
        if self.cache_service:
            conversation_memory = await self.cache_service.get_conversation_memory(
                str(conversation_id)
            ) or {}
            user_summary = await self.cache_service.get_user_conversation_summary(
                str(user_id)
            ) or {}
        
        # Merge conversation-specific insights with user-level patterns
        recurring_themes = []
        if conversation_memory.get("recurring_themes"):
            recurring_themes.extend(conversation_memory["recurring_themes"])
        if user_summary.get("recurring_themes"):
            # Add user-level themes not in current conversation
            user_themes = [t for t in user_summary["recurring_themes"] if t not in recurring_themes]
            recurring_themes.extend(user_themes[:3])  # Limit to top 3 user themes
        
        # Get recent insights from current conversation
        recent_insights = conversation_memory.get("insights", [])
        
        # Build context with memory
        context = {
            "mood_trend": mood_trend,
            "average_mood": round(avg_mood, 1),
            "recurring_themes": recurring_themes,
            "recent_insights": recent_insights[-3:] if recent_insights else [],  # Last 3 insights
            "preferred_mode": user_summary.get("preferred_mode", "listen"),
            "conversation_count": user_summary.get("conversation_count", 0),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Add conversation-specific patterns if available
        if conversation_memory.get("emotional_pattern"):
            context["current_emotional_pattern"] = conversation_memory["emotional_pattern"]
        
        return context
    
    async def _save_messages(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_message: str,
        ai_message: str,
        state: ConversationState
    ):
        """Save messages to database with risk detection"""
        
        # Run risk detection on user message
        risk_analysis = RiskDetector.analyze_message(
            user_message,
            sentiment_score=state["sentiment_score"]
        )
        
        # Save user message with risk indicators
        user_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message,
            sentiment_score=state["sentiment_score"],
            emotion_tags=[state["primary_emotion"]],
            risk_score=risk_analysis['risk_score'],
            risk_indicators=risk_analysis['indicators'],
            requires_escalation=risk_analysis['requires_escalation'],
            message_metadata={
                "crisis_level": state["crisis_level"],
                "risk_level": risk_analysis['risk_level']
            }
        )
        db.add(user_msg)
        
        # Update user risk level if necessary
        if risk_analysis['risk_score'] >= 0.6:
            await self._update_user_risk(
                db,
                conversation_id,
                risk_analysis['risk_score'],
                risk_analysis['risk_level']
            )
        
        # Save assistant message
        ai_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=ai_message,
            message_metadata={
                "mode": state["mode"]
            }
        )
        db.add(ai_msg)
        
        await db.commit()
        
        logger.info(
            f"Saved messages for conversation {conversation_id}: "
            f"sentiment={state['sentiment_score']}, "
            f"risk_score={risk_analysis['risk_score']}, "
            f"risk_level={risk_analysis['risk_level']}, "
            f"requires_escalation={risk_analysis['requires_escalation']}"
        )
        
        # If critical risk detected, log for immediate attention
        if risk_analysis['requires_escalation']:
            logger.warning(
                f"⚠️ HIGH RISK USER DETECTED - Conversation {conversation_id}: "
                f"Risk Level: {risk_analysis['risk_level']}, "
                f"Score: {risk_analysis['risk_score']}, "
                f"Indicators: {risk_analysis['indicators']}"
            )
    
    async def _update_user_risk(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        risk_score: float,
        risk_level: str
    ):
        """Update user's risk level based on conversation analysis"""
        try:
            # Get user from conversation
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return
            
            # Get user
            user_result = await db.execute(
                select(User).where(User.id == conversation.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return
            
            # Get recent risk scores for this user
            recent_messages = await db.execute(
                select(Message.risk_score)
                .join(Conversation)
                .where(
                    Conversation.user_id == user.id,
                    Message.role == MessageRole.USER,
                    Message.risk_score.isnot(None)
                )
                .order_by(desc(Message.created_at))
                .limit(10)
            )
            risk_history = [score for (score,) in recent_messages.all() if score]
            
            # Determine if user risk level should be updated
            should_update, new_risk_level = RiskDetector.should_update_user_risk_level(
                risk_history,
                risk_score
            )
            
            if should_update:
                user.risk_level = new_risk_level
                user.last_risk_assessment = datetime.utcnow()
                
                # Set escalation status if critical
                if new_risk_level in ['high', 'critical'] and not user.escalation_status:
                    user.escalation_status = 'pending'
                
                await db.commit()
                
                logger.warning(
                    f"Updated user {user.id} risk level to {new_risk_level} "
                    f"(score: {risk_score}, history avg: {sum(risk_history)/len(risk_history) if risk_history else 0:.2f})"
                )
        
        except Exception as e:
            logger.error(f"Failed to update user risk level: {e}")
