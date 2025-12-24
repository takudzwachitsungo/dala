"""Safety plan endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.safety_plan import SafetyPlan
from app.schemas.safety_plan import SafetyPlanResponse, SafetyPlanCreate, SafetyPlanUpdate
from app.api.deps import get_current_user


router = APIRouter()


@router.get("", response_model=SafetyPlanResponse)
async def get_safety_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's safety plan"""
    
    result = await db.execute(
        select(SafetyPlan).where(SafetyPlan.user_id == current_user.id)
    )
    safety_plan = result.scalar_one_or_none()
    
    if not safety_plan:
        # Create empty safety plan if doesn't exist
        safety_plan = SafetyPlan(user_id=current_user.id)
        db.add(safety_plan)
        await db.commit()
        await db.refresh(safety_plan)
    
    return safety_plan


@router.put("", response_model=SafetyPlanResponse)
async def update_safety_plan(
    data: SafetyPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's safety plan"""
    
    result = await db.execute(
        select(SafetyPlan).where(SafetyPlan.user_id == current_user.id)
    )
    safety_plan = result.scalar_one_or_none()
    
    if not safety_plan:
        # Create new safety plan
        safety_plan = SafetyPlan(
            user_id=current_user.id,
            **data.model_dump()
        )
        db.add(safety_plan)
    else:
        # Update existing
        for field, value in data.model_dump().items():
            setattr(safety_plan, field, value)
    
    await db.commit()
    await db.refresh(safety_plan)
    
    return safety_plan
