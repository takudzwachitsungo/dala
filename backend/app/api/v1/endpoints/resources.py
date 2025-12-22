from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.resource import Resource
from app.schemas.resource import ResourceResponse, ResourceFilter
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[ResourceResponse])
async def list_resources(
    resource_type: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List resources with optional filters"""
    query = select(Resource)
    
    # Apply filters
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)
    if category:
        query = query.where(Resource.category == category)
    if difficulty:
        query = query.where(Resource.difficulty == difficulty)
    
    # Order by helpful count and view count
    query = query.order_by(
        Resource.helpful_count.desc(),
        Resource.view_count.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resource details and increment view count"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Increment view count
    resource.view_count += 1
    await db.commit()
    await db.refresh(resource)
    
    return resource


@router.post("/{resource_id}/helpful", status_code=status.HTTP_204_NO_CONTENT)
async def mark_helpful(
    resource_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a resource as helpful"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Increment helpful count
    resource.helpful_count += 1
    await db.commit()
