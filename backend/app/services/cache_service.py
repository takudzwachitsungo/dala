"""Redis caching service for sessions, rate limiting, and conversation context"""

import json
from typing import Optional, Any, Dict
from datetime import timedelta
import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class CacheService:
    """Redis caching service"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    # ============= Session Management =============
    
    async def set_session(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        expire: int = 86400
    ):
        """Store user session (24h default)"""
        key = f"session:{user_id}"
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(session_data)
            )
        except Exception as e:
            logger.error(f"Failed to set session: {e}")
    
    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session"""
        key = f"session:{user_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    async def delete_session(self, user_id: str):
        """Delete session on logout"""
        key = f"session:{user_id}"
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
    
    # ============= Rate Limiting =============
    
    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str = "default",
        limit: int = None,
        window: int = None
    ) -> tuple[bool, int]:
        """
        Token bucket rate limiting
        
        Args:
            user_id: User ID
            endpoint: Endpoint identifier
            limit: Max requests (defaults to settings)
            window: Time window in seconds (defaults to settings)
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if limit is None:
            limit = settings.RATE_LIMIT_REQUESTS
        if window is None:
            window = settings.RATE_LIMIT_WINDOW
        
        key = f"ratelimit:{endpoint}:{user_id}"
        
        try:
            # Increment counter
            count = await self.redis.incr(key)
            
            # Set expiry on first request
            if count == 1:
                await self.redis.expire(key, window)
            
            is_allowed = count <= limit
            remaining = max(0, limit - count)
            
            return is_allowed, remaining
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request on error
            return True, limit
    
    async def get_rate_limit_ttl(self, user_id: str, endpoint: str = "default") -> int:
        """Get TTL for rate limit reset"""
        key = f"ratelimit:{endpoint}:{user_id}"
        try:
            ttl = await self.redis.ttl(key)
            return max(0, ttl)
        except Exception as e:
            logger.error(f"Failed to get rate limit TTL: {e}")
            return 0
    
    # ============= Conversation Context Caching =============
    
    async def cache_conversation_context(
        self,
        conversation_id: str,
        context: Dict[str, Any],
        expire: int = None
    ):
        """
        Cache conversation context for quick retrieval
        
        Args:
            conversation_id: Conversation ID
            context: Context data (messages, preferences, themes)
            expire: TTL in seconds (defaults to settings)
        """
        if expire is None:
            expire = settings.CONVERSATION_CONTEXT_TTL
        
        key = f"conv_context:{conversation_id}"
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(context)
            )
        except Exception as e:
            logger.error(f"Failed to cache conversation context: {e}")
    
    async def get_conversation_context(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached conversation context"""
        key = f"conv_context:{conversation_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return None
    
    async def invalidate_conversation_context(self, conversation_id: str):
        """Invalidate conversation context cache"""
        key = f"conv_context:{conversation_id}"
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to invalidate conversation context: {e}")
    
    # ============= Mood Data Caching =============
    
    async def cache_user_mood_summary(
        self,
        user_id: str,
        summary: Dict[str, Any],
        expire: int = 1800
    ):
        """Cache mood summary for 30 minutes"""
        key = f"mood_summary:{user_id}"
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(summary)
            )
        except Exception as e:
            logger.error(f"Failed to cache mood summary: {e}")
    
    async def get_user_mood_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached mood summary"""
        key = f"mood_summary:{user_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get mood summary: {e}")
            return None
    
    async def invalidate_mood_summary(self, user_id: str):
        """Invalidate mood summary cache"""
        key = f"mood_summary:{user_id}"
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to invalidate mood summary: {e}")
    
    # ============= Active User Tracking =============
    
    async def mark_user_active(self, user_id: str):
        """Mark user as active (for analytics)"""
        key = "active_users"
        try:
            await self.redis.sadd(key, user_id)
            await self.redis.expire(key, 300)  # 5 min window
        except Exception as e:
            logger.error(f"Failed to mark user active: {e}")
    
    async def get_active_user_count(self) -> int:
        """Get count of active users"""
        key = "active_users"
        try:
            return await self.redis.scard(key)
        except Exception as e:
            logger.error(f"Failed to get active user count: {e}")
            return 0
    
    # ============= LLM Response Caching (Optional) =============
    
    async def cache_llm_response(
        self,
        prompt_hash: str,
        response: str,
        expire: int = 3600
    ):
        """Cache common LLM responses"""
        key = f"llm_cache:{prompt_hash}"
        try:
            await self.redis.setex(key, expire, response)
        except Exception as e:
            logger.error(f"Failed to cache LLM response: {e}")
    
    async def get_cached_llm_response(self, prompt_hash: str) -> Optional[str]:
        """Get cached LLM response"""
        key = f"llm_cache:{prompt_hash}"
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get cached LLM response: {e}")
            return None
    
    # ============= Phase 3: Conversation Memory =============
    
    async def store_conversation_memory(
        self,
        conversation_id: str,
        memory_data: Dict[str, Any],
        expire: int = 604800  # 7 days
    ):
        """
        Store session-level conversation memory
        
        Includes: Key insights, recurring themes, progress markers
        """
        key = f"conversation_memory:{conversation_id}"
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(memory_data)
            )
            logger.debug(f"Stored conversation memory for {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to store conversation memory: {e}")
    
    async def get_conversation_memory(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve conversation memory"""
        key = f"conversation_memory:{conversation_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get conversation memory: {e}")
            return None
    
    async def update_conversation_memory(
        self,
        conversation_id: str,
        updates: Dict[str, Any]
    ):
        """Update specific fields in conversation memory"""
        try:
            existing = await self.get_conversation_memory(conversation_id) or {}
            existing.update(updates)
            await self.store_conversation_memory(conversation_id, existing)
        except Exception as e:
            logger.error(f"Failed to update conversation memory: {e}")
    
    async def add_to_conversation_insights(
        self,
        conversation_id: str,
        insight: str
    ):
        """Add a new insight to conversation memory"""
        try:
            memory = await self.get_conversation_memory(conversation_id) or {}
            insights = memory.get('insights', [])
            
            # Keep last 10 insights
            insights.append({
                'content': insight,
                'timestamp': str(timedelta())
            })
            insights = insights[-10:]
            
            memory['insights'] = insights
            await self.store_conversation_memory(conversation_id, memory)
        except Exception as e:
            logger.error(f"Failed to add conversation insight: {e}")
    
    async def get_user_conversation_summary(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get aggregated conversation summary across all user conversations
        For AI context: Common themes, progress, preferences
        """
        key = f"user_summary:{user_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else {
                'recurring_themes': [],
                'preferred_mode': 'listen',
                'conversation_count': 0,
                'last_topics': []
            }
        except Exception as e:
            logger.error(f"Failed to get user conversation summary: {e}")
            return {}
    
    async def update_user_summary(
        self,
        user_id: str,
        summary_data: Dict[str, Any],
        expire: int = 2592000  # 30 days
    ):
        """Update user's aggregated conversation summary"""
        key = f"user_summary:{user_id}"
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(summary_data)
            )
        except Exception as e:
            logger.error(f"Failed to update user summary: {e}")
