from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.path import Path, PathStep, UserPathProgress
from app.schemas.path import (
    PathResponse,
    PathDetailResponse,
    PathStepResponse,
    UserPathProgressResponse,
    PathProgressUpdate,
    StepReflectionCreate
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[PathResponse])
async def list_paths(
    category: str = None,
    difficulty: str = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available paths"""
    query = select(Path)
    
    if category:
        query = query.where(Path.category == category)
    if difficulty:
        query = query.where(Path.difficulty == difficulty)
    
    query = query.order_by(Path.enrollment_count.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    paths = result.scalars().all()
    
    return paths


@router.get("/{path_id}", response_model=PathDetailResponse)
async def get_path_detail(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get path details with steps and user progress"""
    # Get path with steps
    result = await db.execute(
        select(Path)
        .options(selectinload(Path.steps))
        .where(Path.id == path_id)
    )
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    
    # Get user progress if enrolled
    progress_result = await db.execute(
        select(UserPathProgress).where(
            and_(
                UserPathProgress.path_id == path_id,
                UserPathProgress.user_id == current_user.id
            )
        )
    )
    user_progress = progress_result.scalar_one_or_none()
    
    # Build response
    path_dict = PathResponse.model_validate(path).model_dump()
    
    # Sort steps by order
    steps = sorted(path.steps, key=lambda s: s.order_index)
    path_dict["steps"] = [PathStepResponse.model_validate(s) for s in steps]
    
    if user_progress:
        path_dict["user_progress"] = UserPathProgressResponse.model_validate(user_progress)
    else:
        path_dict["user_progress"] = None
    
    return PathDetailResponse(**path_dict)


@router.post("/{path_id}/enroll", response_model=UserPathProgressResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enroll in a path"""
    # Check path exists
    result = await db.execute(select(Path).where(Path.id == path_id))
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    
    # Check not already enrolled
    progress_result = await db.execute(
        select(UserPathProgress).where(
            and_(
                UserPathProgress.path_id == path_id,
                UserPathProgress.user_id == current_user.id
            )
        )
    )
    if progress_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this path"
        )
    
    # Create progress record
    progress = UserPathProgress(
        user_id=current_user.id,
        path_id=path_id,
        current_step_index=0,
        completed_steps={},
        reflection_logs={}
    )
    db.add(progress)
    
    # Update enrollment count
    path.enrollment_count += 1
    
    await db.commit()
    await db.refresh(progress)
    
    return progress


@router.patch("/{path_id}/progress", response_model=UserPathProgressResponse)
async def update_progress(
    path_id: UUID,
    update_data: PathProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update path progress"""
    # Get progress record
    result = await db.execute(
        select(UserPathProgress).where(
            and_(
                UserPathProgress.path_id == path_id,
                UserPathProgress.user_id == current_user.id
            )
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this path"
        )
    
    # Get path to check step count
    path_result = await db.execute(select(Path).where(Path.id == path_id))
    path = path_result.scalar_one()
    
    # Update progress
    progress.current_step_index = update_data.current_step_index
    progress.last_activity = datetime.utcnow()
    
    if update_data.completed_steps:
        progress.completed_steps = update_data.completed_steps
    
    # Calculate progress percentage
    if path.step_count > 0:
        completed_count = len(progress.completed_steps or {})
        progress.progress_percentage = (completed_count / path.step_count) * 100
        
        # Check if completed
        if completed_count >= path.step_count:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(progress)
    
    return progress


@router.post("/{path_id}/reflections", status_code=status.HTTP_204_NO_CONTENT)
async def save_step_reflection(
    path_id: UUID,
    reflection_data: StepReflectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save reflection for a step"""
    # Get progress record
    result = await db.execute(
        select(UserPathProgress).where(
            and_(
                UserPathProgress.path_id == path_id,
                UserPathProgress.user_id == current_user.id
            )
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this path"
        )
    
    # Add reflection to logs
    if not progress.reflection_logs:
        progress.reflection_logs = {}
    
    progress.reflection_logs[str(reflection_data.step_id)] = {
        "reflection": reflection_data.reflection,
        "mood_rating": reflection_data.mood_rating,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Mark step as completed
    if not progress.completed_steps:
        progress.completed_steps = {}
    
    progress.completed_steps[str(reflection_data.step_id)] = {
        "completed_at": datetime.utcnow().isoformat()
    }
    
    progress.last_activity = datetime.utcnow()
    
    await db.commit()
