"""Mood tracking endpoints"""

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from statistics import mean

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.mood import MoodEntry
from app.db.models.milestone import UserMilestone
from app.schemas.mood import MoodEntryCreate, MoodEntryResponse, MoodHistoryResponse
from app.api.deps import get_current_user


router = APIRouter()


@router.post("", response_model=MoodEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_entry(
    data: MoodEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log a mood entry"""
    
    entry = MoodEntry(
        user_id=current_user.id,
        mood_score=data.mood_score,
        emotions=data.emotions or [],
        activities=data.activities or [],
        notes=data.notes,
        conversation_id=data.conversation_id
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    # Check for milestones
    await _check_mood_milestones(current_user.id, db)
    
    return MoodEntryResponse.model_validate(entry)


@router.get("/history", response_model=MoodHistoryResponse)
async def get_mood_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get mood history for specified days"""
    
    if days < 1 or days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 90"
        )
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(MoodEntry)
        .where(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= cutoff_date
        )
        .order_by(desc(MoodEntry.created_at))
    )
    entries = result.scalars().all()
    
    if not entries:
        return MoodHistoryResponse(
            entries=[],
            average_score=0.0,
            trend="stable",
            total_entries=0
        )
    
    # Calculate average
    scores = [entry.mood_score for entry in entries]
    average_score = mean(scores)
    
    # Calculate trend (compare first half to second half)
    mid_point = len(scores) // 2
    if mid_point > 0:
        first_half_avg = mean(scores[:mid_point])
        second_half_avg = mean(scores[mid_point:])
        
        if second_half_avg > first_half_avg + 0.5:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return MoodHistoryResponse(
        entries=[MoodEntryResponse.model_validate(e) for e in entries],
        average_score=round(average_score, 2),
        trend=trend,
        total_entries=len(entries)
    )


async def _check_mood_milestones(user_id, db: AsyncSession):
    """Check and award mood-related milestones"""
    
    # Check for first check-in milestone
    result = await db.execute(
        select(func.count(MoodEntry.id))
        .where(MoodEntry.user_id == user_id)
    )
    entry_count = result.scalar()
    
    if entry_count == 1:
        # Award first check-in milestone
        existing = await db.execute(
            select(UserMilestone).where(
                UserMilestone.user_id == user_id,
                UserMilestone.milestone_type == "first_checkin"
            )
        )
        if not existing.scalar_one_or_none():
            milestone = UserMilestone(
                user_id=user_id,
                milestone_type="first_checkin"
            )
            db.add(milestone)
    
    # Check for streak milestones
    # Get last 7 days of entries
    cutoff = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(func.date(MoodEntry.created_at))
        .where(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= cutoff
        )
        .distinct()
        .order_by(desc(func.date(MoodEntry.created_at)))
    )
    dates = [row[0] for row in result.fetchall()]
    
    # Calculate consecutive days
    streak = 0
    current_date = datetime.utcnow().date()
    for date in dates:
        if date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break
    
    # Award streak milestones
    if streak >= 3:
        existing = await db.execute(
            select(UserMilestone).where(
                UserMilestone.user_id == user_id,
                UserMilestone.milestone_type == "three_day_streak"
            )
        )
        if not existing.scalar_one_or_none():
            milestone = UserMilestone(
                user_id=user_id,
                milestone_type="three_day_streak"
            )
            db.add(milestone)
    
    if streak >= 7:
        existing = await db.execute(
            select(UserMilestone).where(
                UserMilestone.user_id == user_id,
                UserMilestone.milestone_type == "week_streak"
            )
        )
        if not existing.scalar_one_or_none():
            milestone = UserMilestone(
                user_id=user_id,
                milestone_type="week_streak"
            )
            db.add(milestone)
    
    await db.commit()
