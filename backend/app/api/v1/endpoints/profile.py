"""Profile endpoints"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.mood import MoodEntry
from app.db.models.conversation import Conversation
from app.db.models.milestone import UserMilestone
from app.schemas.profile import ProfileResponse, MilestoneResponse
from app.schemas.user import UserUpdate
from app.api.deps import get_current_user


router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile with stats"""
    
    # Calculate streak
    streak_days = await _calculate_streak(current_user.id, db)
    
    # Get total mood entries
    result = await db.execute(
        select(func.count(MoodEntry.id))
        .where(MoodEntry.user_id == current_user.id)
    )
    total_mood_entries = result.scalar()
    
    # Get total conversations
    result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == current_user.id)
    )
    total_conversations = result.scalar()
    
    # Get milestones
    result = await db.execute(
        select(UserMilestone)
        .where(UserMilestone.user_id == current_user.id)
        .order_by(UserMilestone.earned_at.desc())
    )
    milestones = result.scalars().all()
    
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        streak_days=streak_days,
        total_mood_entries=total_mood_entries,
        total_conversations=total_conversations,
        milestone_count=len(milestones),
        milestones=[MilestoneResponse.model_validate(m) for m in milestones],
        is_admin=current_user.is_admin,
        is_anonymous=current_user.is_anonymous,
        role=current_user.role
    )


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    
    # Check username uniqueness if changing
    if data.username and data.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        current_user.username = data.username
    
    # Check email uniqueness if changing
    if data.email and data.email != current_user.email:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        current_user.email = data.email
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    # Return updated profile
    return await get_profile(current_user, db)


@router.get("/milestones", response_model=list[MilestoneResponse])
async def get_milestones(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all user milestones"""
    
    result = await db.execute(
        select(UserMilestone)
        .where(UserMilestone.user_id == current_user.id)
        .order_by(UserMilestone.earned_at.desc())
    )
    milestones = result.scalars().all()
    
    return [MilestoneResponse.model_validate(m) for m in milestones]


async def _calculate_streak(user_id, db: AsyncSession) -> int:
    """Calculate current mood check-in streak"""
    
    # Get last 30 days of entries
    cutoff = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.date(MoodEntry.created_at))
        .where(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= cutoff
        )
        .distinct()
        .order_by(func.date(MoodEntry.created_at).desc())
    )
    dates = [row[0] for row in result.fetchall()]
    
    if not dates:
        return 0
    
    # Calculate consecutive days from today
    streak = 0
    current_date = datetime.utcnow().date()
    
    for date in dates:
        expected_date = current_date - timedelta(days=streak)
        if date == expected_date:
            streak += 1
        else:
            break
    
    return streak
