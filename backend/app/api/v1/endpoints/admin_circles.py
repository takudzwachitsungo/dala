"""Admin endpoints for circle management"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.circle import Circle, CircleMembership
from app.schemas.circle import CircleCreate, CircleResponse
from app.api.deps import get_current_user

router = APIRouter()


async def require_moderator(current_user: User = Depends(get_current_user)):
    """Verify user is a moderator or admin"""
    if not (current_user.is_moderator or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access required"
        )
    return current_user


@router.post("/circles", response_model=CircleResponse, status_code=status.HTTP_201_CREATED)
async def create_circle(
    circle: CircleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Create a new circle (moderator only)"""
    # Create circle
    new_circle = Circle(
        name=circle.name,
        topic=circle.topic,
        description=circle.description,
        icon=circle.icon
    )
    db.add(new_circle)
    await db.flush()
    
    # Auto-join creator as moderator
    membership = CircleMembership(
        circle_id=new_circle.id,
        user_id=current_user.id,
        is_moderator=True
    )
    db.add(membership)
    new_circle.member_count = 1
    
    await db.commit()
    await db.refresh(new_circle)
    
    return new_circle


@router.patch("/circles/{circle_id}", response_model=CircleResponse)
async def update_circle(
    circle_id: UUID,
    circle_update: CircleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Update circle details (moderator only)"""
    result = await db.execute(select(Circle).where(Circle.id == circle_id))
    circle = result.scalar_one_or_none()
    
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    
    # Update fields
    circle.name = circle_update.name
    circle.topic = circle_update.topic
    circle.description = circle_update.description
    if circle_update.icon:
        circle.icon = circle_update.icon
    
    await db.commit()
    await db.refresh(circle)
    
    return circle


@router.delete("/circles/{circle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_circle(
    circle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Delete a circle (moderator only)"""
    result = await db.execute(select(Circle).where(Circle.id == circle_id))
    circle = result.scalar_one_or_none()
    
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    
    await db.delete(circle)
    await db.commit()


@router.get("/circles/stats", response_model=List[dict])
async def get_circle_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Get statistics for all circles"""
    result = await db.execute(
        select(Circle)
        .order_by(Circle.member_count.desc())
    )
    circles = result.scalars().all()
    
    stats = []
    for circle in circles:
        stats.append({
            "id": str(circle.id),
            "name": circle.name,
            "topic": circle.topic,
            "member_count": circle.member_count,
            "post_count": circle.post_count,
            "created_at": circle.created_at.isoformat()
        })
    
    return stats
