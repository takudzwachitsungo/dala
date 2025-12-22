from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.circle import Circle, CircleMembership
from app.db.models.post import Post
from app.schemas.circle import (
    CircleCreate,
    CircleResponse,
    CircleWithMembershipResponse,
    CircleMembershipResponse
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[CircleWithMembershipResponse])
async def list_circles(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all circles with user's membership status"""
    # Get circles
    result = await db.execute(
        select(Circle)
        .order_by(Circle.member_count.desc())
        .offset(skip)
        .limit(limit)
    )
    circles = result.scalars().all()
    
    # Get user's memberships
    membership_result = await db.execute(
        select(CircleMembership)
        .where(CircleMembership.user_id == current_user.id)
    )
    memberships = {m.circle_id: m for m in membership_result.scalars().all()}
    
    # Build response
    response = []
    for circle in circles:
        circle_dict = CircleResponse.model_validate(circle).model_dump()
        membership = memberships.get(circle.id)
        circle_dict["is_member"] = membership is not None
        circle_dict["is_moderator"] = membership.is_moderator if membership else False
        response.append(CircleWithMembershipResponse(**circle_dict))
    
    return response


@router.post("", response_model=CircleResponse, status_code=status.HTTP_201_CREATED)
async def create_circle(
    circle_data: CircleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new circle (creator becomes moderator)"""
    # Check if circle with same name exists
    result = await db.execute(
        select(Circle).where(Circle.name == circle_data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Circle with this name already exists"
        )
    
    # Create circle
    circle = Circle(**circle_data.model_dump())
    circle.member_count = 1
    db.add(circle)
    await db.flush()
    
    # Add creator as moderator
    membership = CircleMembership(
        user_id=current_user.id,
        circle_id=circle.id,
        is_moderator=True
    )
    db.add(membership)
    await db.commit()
    await db.refresh(circle)
    
    return circle


@router.get("/{circle_id}", response_model=CircleWithMembershipResponse)
async def get_circle(
    circle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get circle details with user's membership status"""
    result = await db.execute(
        select(Circle).where(Circle.id == circle_id)
    )
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    
    # Check membership
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    membership = membership_result.scalar_one_or_none()
    
    circle_dict = CircleResponse.model_validate(circle).model_dump()
    circle_dict["is_member"] = membership is not None
    circle_dict["is_moderator"] = membership.is_moderator if membership else False
    
    return CircleWithMembershipResponse(**circle_dict)


@router.post("/{circle_id}/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_circle(
    circle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a circle"""
    # Check circle exists
    result = await db.execute(select(Circle).where(Circle.id == circle_id))
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    
    # Check not already member
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member"
        )
    
    # Join
    membership = CircleMembership(user_id=current_user.id, circle_id=circle_id)
    circle.member_count += 1
    db.add(membership)
    await db.commit()


@router.delete("/{circle_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_circle(
    circle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave a circle"""
    # Get membership
    result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a member"
        )
    
    # Update circle count
    circle_result = await db.execute(select(Circle).where(Circle.id == circle_id))
    circle = circle_result.scalar_one()
    circle.member_count = max(0, circle.member_count - 1)
    
    # Delete membership
    await db.delete(membership)
    await db.commit()


@router.get("/{circle_id}/members", response_model=List[CircleMembershipResponse])
async def list_circle_members(
    circle_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List circle members (requires membership)"""
    # Check circle exists and user is member
    membership_check = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if not membership_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a member to view members"
        )
    
    # Get members
    result = await db.execute(
        select(CircleMembership)
        .where(CircleMembership.circle_id == circle_id)
        .order_by(CircleMembership.is_moderator.desc(), CircleMembership.joined_at)
        .offset(skip)
        .limit(limit)
    )
    members = result.scalars().all()
    
    return members
