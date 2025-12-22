"""WebSocket endpoint for real-time AI chat with LangGraph integration"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from uuid import UUID
from loguru import logger

from app.db.session import AsyncSessionLocal
from app.db.models.conversation import Conversation
from app.api.deps import get_current_user_ws
from app.services.conversation_service import ConversationService
from app.services.cache_service import CacheService
from app.utils.websocket_manager import ws_manager


router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str,
    conversation_id: str,
):
    """
    WebSocket endpoint for real-time AI chat
    
    Query params:
        token: JWT access token
        conversation_id: Conversation UUID
    """
    
    user = None
    user_id = None
    
    try:
        # Create database session
        async with AsyncSessionLocal() as db:
            # Authenticate user
            user = await get_current_user_ws(token, db)
            
            if not user:
                await websocket.accept()
                await websocket.send_json({
                    "type": "error",
                    "message": "Authentication failed"
                })
                await websocket.close(code=4001)
                return
            
            user_id = str(user.id)
            
            # Verify conversation belongs to user
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == UUID(conversation_id),
                    Conversation.user_id == user.id
                )
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                await websocket.accept()
                await websocket.send_json({
                    "type": "error",
                    "message": "Conversation not found"
                })
                await websocket.close(code=4004)
                return
        
        # Connect WebSocket
        await ws_manager.connect(websocket, user_id)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to Dala in {conversation.mode.value} mode",
            "conversation_id": conversation_id,
            "mode": conversation.mode.value
        })
        
        logger.info(f"User {user_id} connected to conversation {conversation_id}")
        
        # Initialize services
        cache_service = CacheService(websocket.app.state.redis)
        conversation_service = ConversationService(cache_service)
        
        # Mark user as active
        await cache_service.mark_user_active(user_id)
        
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type", "message")
            
            if message_type == "message":
                user_message = message_data.get("message", "")
                mode = message_data.get("mode", conversation.mode.value)
                
                if not user_message.strip():
                    await websocket.send_json({
                        "type": "error",
                        "message": "Empty message"
                    })
                    continue
                
                # Check rate limit
                is_allowed, remaining = await cache_service.check_rate_limit(
                    user_id=user_id,
                    endpoint="chat",
                    limit=60,  # 60 messages per minute
                    window=60
                )
                
                if not is_allowed:
                    ttl = await cache_service.get_rate_limit_ttl(user_id, "chat")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Rate limit exceeded. Please wait {ttl} seconds.",
                        "retry_after": ttl
                    })
                    continue
                
                # Send typing indicator
                await websocket.send_json({
                    "type": "typing",
                    "status": True
                })
                
                # Stream AI response
                async with AsyncSessionLocal() as db:
                    async for chunk in conversation_service.stream_conversation(
                        db=db,
                        user_id=user.id,
                        conversation_id=UUID(conversation_id),
                        message=user_message,
                        mode=mode
                    ):
                        await websocket.send_json(chunk)
                
                # Stop typing indicator
                await websocket.send_json({
                    "type": "typing",
                    "status": False
                })
                
            elif message_type == "ping":
                # Keep-alive ping
                await websocket.send_json({
                    "type": "pong"
                })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
        if user_id:
            ws_manager.disconnect(websocket, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": "An unexpected error occurred"
            })
            await websocket.close(code=1011)
        except:
            pass
        
        if user_id:
            ws_manager.disconnect(websocket, user_id)
