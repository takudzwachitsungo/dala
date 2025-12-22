"""LLM Client with GroqCloud primary and MiniMax fallback"""

from typing import AsyncGenerator, List, Dict, Any
from groq import AsyncGroq, RateLimitError, APIError
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class LLMClient:
    """LLM client with GroqCloud primary and MiniMax fallback"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.minimax_api_key = settings.MINIMAX_API_KEY
        self.groq_model = "llama-3.3-70b-versatile"  # Updated model
        self.groq_fast_model = "llama-3.1-8b-instant"
        self.use_fallback = False
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream response from LLM with automatic fallback
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Dict with 'content' and 'done' keys
        """
        try:
            # Try GroqCloud first
            async for chunk in self._groq_stream(messages, temperature, max_tokens):
                yield chunk
                
        except (RateLimitError, APIError) as e:
            logger.warning(f"GroqCloud error: {e}. Falling back to MiniMax...")
            
            if self.minimax_api_key:
                try:
                    async for chunk in self._minimax_stream(messages, temperature, max_tokens):
                        yield chunk
                except Exception as minimax_error:
                    logger.error(f"MiniMax fallback failed: {minimax_error}")
                    yield {
                        "content": "I'm having trouble connecting right now. Please try again in a moment.",
                        "done": True,
                        "error": True
                    }
            else:
                yield {
                    "content": "I'm experiencing high demand. Please try again shortly.",
                    "done": True,
                    "error": True
                }
    
    async def _groq_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream from GroqCloud"""
        
        stream = await self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {
                    "content": chunk.choices[0].delta.content,
                    "done": False,
                    "provider": "groq"
                }
        
        yield {
            "content": "",
            "done": True,
            "provider": "groq"
        }
    
    async def _minimax_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream from MiniMax API (if available)"""
        
        # MiniMax API implementation
        # Note: This is a placeholder - adjust based on actual MiniMax API
        
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "abab6.5-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=data, headers=headers) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        content = line[6:]  # Remove "data: " prefix
                        if content and content != "[DONE]":
                            import json
                            try:
                                chunk_data = json.loads(content)
                                if "choices" in chunk_data:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield {
                                            "content": delta["content"],
                                            "done": False,
                                            "provider": "minimax"
                                        }
                            except json.JSONDecodeError:
                                continue
        
        yield {
            "content": "",
            "done": True,
            "provider": "minimax"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate response (non-streaming) with retry logic
        
        Args:
            messages: List of message dicts
            temperature: Generation temperature
            max_tokens: Maximum tokens
            
        Returns:
            Generated text response
        """
        try:
            response = await self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except (RateLimitError, APIError) as e:
            logger.warning(f"GroqCloud error in generate: {e}")
            
            if self.minimax_api_key:
                # Fallback to MiniMax
                return await self._minimax_generate(messages, temperature, max_tokens)
            else:
                raise
    
    async def _minimax_generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate from MiniMax (non-streaming)"""
        
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "abab6.5-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def quick_analysis(
        self,
        prompt: str,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Quick analysis using fast model for routing decisions
        
        Args:
            prompt: Analysis prompt
            temperature: Lower temperature for more deterministic output
            
        Returns:
            JSON response
        """
        try:
            response = await self.groq_client.chat.completions.create(
                model=self.groq_fast_model,  # Use faster model
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=256,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Quick analysis failed: {e}")
            # Return safe defaults
            return {
                "primary_emotion": "neutral",
                "urgency": 5,
                "topics": [],
                "needs": []
            }
