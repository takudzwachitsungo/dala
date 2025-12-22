"""Admin endpoints for path management"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.path import Path, PathStep
from app.schemas.path import PathBase, PathResponse, PathStepBase
from app.api.deps import get_current_user
from app.api.v1.endpoints.admin_circles import require_moderator

router = APIRouter()


class PathCreateRequest(PathBase):
    steps: List[PathStepBase] = []


@router.post("/paths", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
async def create_path(
    path_data: PathCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Create a new guided path with steps (moderator only)"""
    # Create path
    new_path = Path(
        name=path_data.name,
        description="",  # Will be updated with steps
        category=path_data.category,
        difficulty=path_data.difficulty,
        estimated_duration=path_data.estimated_duration,
        step_count=len(path_data.steps) if hasattr(path_data, 'steps') else 0
    )
    db.add(new_path)
    await db.flush()
    
    # Add steps if provided
    if hasattr(path_data, 'steps') and path_data.steps:
        for idx, step_data in enumerate(path_data.steps):
            step = PathStep(
                path_id=new_path.id,
                order_index=idx,
                title=step_data.title,
                description="",
                content=step_data.content,
                step_type=step_data.step_type,
                estimated_minutes=step_data.estimated_minutes
            )
            db.add(step)
    
    await db.commit()
    await db.refresh(new_path)
    
    return new_path


@router.patch("/paths/{path_id}", response_model=PathResponse)
async def update_path(
    path_id: UUID,
    path_update: PathBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Update path details (moderator only)"""
    result = await db.execute(select(Path).where(Path.id == path_id))
    path = result.scalar_one_or_none()
    
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    
    # Update fields
    path.name = path_update.name
    path.category = path_update.category
    path.difficulty = path_update.difficulty
    if path_update.estimated_duration:
        path.estimated_duration = path_update.estimated_duration
    
    await db.commit()
    await db.refresh(path)
    
    return path


@router.delete("/paths/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Delete a path (moderator only)"""
    result = await db.execute(select(Path).where(Path.id == path_id))
    path = result.scalar_one_or_none()
    
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    
    await db.delete(path)
    await db.commit()


@router.patch("/paths/{path_id}/publish")
async def toggle_path_publish(
    path_id: UUID,
    is_published: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """Publish or unpublish a path"""
    result = await db.execute(select(Path).where(Path.id == path_id))
    path = result.scalar_one_or_none()
    
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    
    path.is_published = is_published
    await db.commit()
    
    return {"message": f"Path {'published' if is_published else 'unpublished'} successfully"}
