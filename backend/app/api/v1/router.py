"""Main API router"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, conversations, mood, profile, websocket,
    circles, posts, paths, resources, admin,
    admin_circles, admin_paths
)


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(mood.router, prefix="/mood", tags=["Mood Tracking"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(websocket.router, tags=["WebSocket"])

# Phase 2: Community & Guided Paths
api_router.include_router(circles.router, prefix="/circles", tags=["Circles"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
api_router.include_router(paths.router, prefix="/paths", tags=["Paths"])
api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Phase 3: Admin Management
api_router.include_router(admin_circles.router, prefix="/admin", tags=["Admin - Circles"])
api_router.include_router(admin_paths.router, prefix="/admin", tags=["Admin - Paths"])
