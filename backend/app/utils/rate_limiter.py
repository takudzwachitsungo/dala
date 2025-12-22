"""Rate limiting utilities"""

from fastapi import HTTPException, status, Request
from app.services.cache_service import CacheService


async def rate_limit_check(
    request: Request,
    user_id: str,
    endpoint: str = "default",
    limit: int = None,
    window: int = None
):
    """
    Check rate limit for user
    
    Raises HTTPException if rate limit exceeded
    """
    cache_service = CacheService(request.app.state.redis)
    
    is_allowed, remaining = await cache_service.check_rate_limit(
        user_id=user_id,
        endpoint=endpoint,
        limit=limit,
        window=window
    )
    
    if not is_allowed:
        ttl = await cache_service.get_rate_limit_ttl(user_id, endpoint)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
            headers={
                "Retry-After": str(ttl),
                "X-RateLimit-Remaining": "0"
            }
        )
    
    # Add rate limit headers to response (will be added by middleware)
    request.state.rate_limit_remaining = remaining
    
    return True
