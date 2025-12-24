from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, String
from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.post import Post
from app.db.models.circle import Circle
from app.db.models.path import Path, UserPathProgress
from app.db.models.mood import MoodEntry
from app.db.models.conversation import Conversation
from app.schemas.post import PostResponse
from app.api.deps import get_current_user

router = APIRouter()


async def verify_admin(current_user: User = Depends(get_current_user)):
    """Verify user has admin or moderator privileges"""
    if not current_user or current_user.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    if not (current_user.is_admin or current_user.is_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or moderator access required"
        )
    return current_user


@router.get("/posts/flagged", response_model=List[PostResponse])
async def list_flagged_posts(
    severity: str = None,  # Filter by severity: low, medium, high, critical
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """List flagged posts with optional severity filter"""
    query = select(Post).where(Post.is_flagged == True)
    
    if severity:
        query = query.where(Post.flag_severity == severity)
    
    query = query.order_by(
        # Critical first, then by creation date
        Post.flag_severity.desc(),
        Post.created_at.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    response = []
    for post in posts:
        post_dict = PostResponse.model_validate(post).model_dump()
        post_dict["author_name"] = "Anonymous" if post.is_anonymous else f"User {post.user_id}"
        response.append(PostResponse(**post_dict))
    
    return response


@router.patch("/posts/{post_id}/hide", status_code=status.HTTP_204_NO_CONTENT)
async def hide_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Hide a flagged post and mark as reviewed"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    post.is_hidden = True
    post.reviewed_by_id = current_user.id
    post.reviewed_at = datetime.utcnow()
    await db.commit()


@router.patch("/posts/{post_id}/unhide", status_code=status.HTTP_204_NO_CONTENT)
async def unhide_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Unhide a post"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    post.is_hidden = False
    post.is_flagged = False
    await db.commit()


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Get platform analytics"""
    # User stats
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    registered_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_anonymous == False)
    )
    registered_users = registered_users_result.scalar()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )
    new_users_week = new_users_result.scalar()
    
    # Circle stats
    total_circles_result = await db.execute(select(func.count(Circle.id)))
    total_circles = total_circles_result.scalar()
    
    # Post stats
    total_posts_result = await db.execute(select(func.count(Post.id)))
    total_posts = total_posts_result.scalar()
    
    flagged_posts_result = await db.execute(
        select(func.count(Post.id)).where(Post.is_flagged == True)
    )
    flagged_posts = flagged_posts_result.scalar()
    
    # Path stats
    total_paths_result = await db.execute(select(func.count(Path.id)))
    total_paths = total_paths_result.scalar()
    
    active_enrollments_result = await db.execute(
        select(func.count(UserPathProgress.id)).where(
            UserPathProgress.is_completed == False
        )
    )
    active_enrollments = active_enrollments_result.scalar()
    
    # Mood tracking stats
    total_moods_result = await db.execute(select(func.count(MoodEntry.id)))
    total_moods = total_moods_result.scalar()
    
    avg_mood_result = await db.execute(
        select(func.avg(MoodEntry.mood_score)).where(
            MoodEntry.created_at >= week_ago
        )
    )
    avg_mood_week = avg_mood_result.scalar() or 0
    
    # Conversation stats
    total_conversations_result = await db.execute(select(func.count(Conversation.id)))
    total_conversations = total_conversations_result.scalar()
    
    return {
        "users": {
            "total": total_users,
            "registered": registered_users,
            "anonymous": total_users - registered_users,
            "new_this_week": new_users_week
        },
        "circles": {
            "total": total_circles
        },
        "posts": {
            "total": total_posts,
            "flagged": flagged_posts
        },
        "paths": {
            "total": total_paths,
            "active_enrollments": active_enrollments
        },
        "mood_tracking": {
            "total_entries": total_moods,
            "avg_mood_this_week": round(float(avg_mood_week), 2)
        },
        "conversations": {
            "total": total_conversations
        }
    }


# Phase 3: User Management & Risk Assessment

@router.get("/users")
async def list_all_users(
    search: str = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """List all users with optional search"""
    query = select(User)
    
    if search:
        query = query.where(
            (User.username.ilike(f"%{search}%")) | 
            (User.id.cast(String).ilike(f"%{search}%"))
        )
    
    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Get flag counts for each user
    from app.db.models.post import Post
    user_data = []
    for user in users:
        # Count flagged posts by this user
        flag_result = await db.execute(
            select(func.count(Post.id))
            .where(Post.user_id == user.id, Post.is_flagged == True)
        )
        flag_count = flag_result.scalar() or 0
        
        user_data.append({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "is_moderator": user.is_moderator,
            "is_anonymous": user.is_anonymous,
            "risk_level": user.risk_level,
            "escalation_status": user.escalation_status,
            "created_at": user.created_at.isoformat(),
            "flag_count": flag_count
        })
    
    return user_data


@router.get("/users/at-risk")
async def get_at_risk_users(
    risk_level: str = "high",  # medium, high, critical
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Get list of users flagged for elevated risk"""
    result = await db.execute(
        select(User)
        .where(User.risk_level.in_(['high', 'critical'] if risk_level == 'high' else [risk_level]))
        .order_by(User.last_risk_assessment.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": str(user.id),
            "username": user.username,
            "risk_level": user.risk_level,
            "escalation_status": user.escalation_status,
            "last_risk_assessment": user.last_risk_assessment.isoformat() if user.last_risk_assessment else None,
            "is_anonymous": user.is_anonymous
        }
        for user in users
    ]


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role: str,  # user, moderator, peer_supporter
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Update user role (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.role = role
    user.is_moderator = role == 'moderator'
    user.is_peer_supporter = role in ['peer_supporter', 'moderator']
    
    await db.commit()
    
    return {"message": f"User role updated to {role}"}


@router.patch("/users/{user_id}/escalation")
async def update_escalation_status(
    user_id: UUID,
    status_update: str,  # pending, escalated, resolved
    notes: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Update user escalation status"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.escalation_status = status_update
    if notes:
        user.moderation_notes = notes
    
    await db.commit()
    
    return {"message": f"Escalation status updated to {status_update}"}


@router.get("/moderation/summary")
async def get_moderation_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Get summary of moderation queue"""
    # Flagged posts by severity
    critical_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.is_flagged == True,
            Post.flag_severity == 'critical'
        )
    )
    critical_count = critical_result.scalar() or 0
    
    high_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.is_flagged == True,
            Post.flag_severity == 'high'
        )
    )
    high_count = high_result.scalar() or 0
    
    medium_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.is_flagged == True,
            Post.flag_severity == 'medium'
        )
    )
    medium_count = medium_result.scalar() or 0
    
    low_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.is_flagged == True,
            Post.flag_severity == 'low'
        )
    )
    low_count = low_result.scalar() or 0
    
    # At-risk users
    high_risk_result = await db.execute(
        select(func.count(User.id)).where(User.risk_level == 'high')
    )
    high_risk_count = high_risk_result.scalar() or 0
    
    critical_risk_result = await db.execute(
        select(func.count(User.id)).where(User.risk_level == 'critical')
    )
    critical_risk_count = critical_risk_result.scalar() or 0
    
    # Pending escalations
    pending_result = await db.execute(
        select(func.count(User.id)).where(User.escalation_status == 'pending')
    )
    pending_count = pending_result.scalar() or 0
    
    # Calculate stats for SystemMonitoring page
    total_flagged = critical_count + high_count + medium_count + low_count
    
    return {
        "total_flagged_posts": total_flagged,
        "pending_review": total_flagged,  # Assuming all flagged posts need review
        "actioned_today": 0,  # Would need to track this in the database
        "high_severity_count": critical_count + high_count,
        "flagged_posts": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "total": total_flagged
        },
        "at_risk_users": {
            "high": high_risk_count,
            "critical": critical_risk_count,
            "total": high_risk_count + critical_risk_count
        },
        "pending_escalations": pending_count
    }


# Phase 4: Path Management

@router.get("/paths")
async def list_all_paths(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """List all paths for admin management"""
    result = await db.execute(
        select(Path)
        .order_by(Path.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    paths = result.scalars().all()
    
    return [
        {
            "id": str(path.id),
            "name": path.name,
            "category": path.category,
            "difficulty": path.difficulty,
            "step_count": path.step_count,
            "enrollment_count": path.enrollment_count,
            "estimated_duration": path.estimated_duration,
            "is_published": path.is_published,
            "created_at": path.created_at.isoformat()
        }
        for path in paths
    ]


@router.post("/paths")
async def create_path(
    path_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Create a new path"""
    new_path = Path(
        name=path_data["name"],
        category=path_data["category"],
        difficulty=path_data.get("difficulty", "beginner"),
        description=path_data.get("description", ""),
        estimated_duration=path_data.get("estimated_duration"),
        step_count=0,
        enrollment_count=0,
        is_published=path_data.get("is_published", False)
    )
    
    db.add(new_path)
    await db.commit()
    await db.refresh(new_path)
    
    return {
        "id": str(new_path.id),
        "name": new_path.name,
        "category": new_path.category,
        "difficulty": new_path.difficulty,
        "step_count": new_path.step_count,
        "enrollment_count": new_path.enrollment_count,
        "is_published": new_path.is_published,
        "created_at": new_path.created_at.isoformat()
    }


@router.patch("/paths/{path_id}")
async def update_path(
    path_id: UUID,
    path_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Update a path"""
    result = await db.execute(select(Path).where(Path.id == path_id))
    path = result.scalar_one_or_none()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    if "name" in path_data:
        path.name = path_data["name"]
    if "category" in path_data:
        path.category = path_data["category"]
    if "difficulty" in path_data:
        path.difficulty = path_data["difficulty"]
    if "description" in path_data:
        path.description = path_data["description"]
    if "estimated_duration" in path_data:
        path.estimated_duration = path_data["estimated_duration"]
    if "is_published" in path_data:
        path.is_published = path_data["is_published"]
    
    await db.commit()
    await db.refresh(path)
    
    return {
        "id": str(path.id),
        "name": path.name,
        "category": path.category,
        "difficulty": path.difficulty,
        "is_published": path.is_published,
        "updated_at": datetime.utcnow().isoformat()
    }


@router.delete("/paths/{path_id}")
async def delete_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Delete a path"""
    result = await db.execute(select(Path).where(Path.id == path_id))
    path = result.scalar_one_or_none()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    await db.delete(path)
    await db.commit()
    
    return {"message": "Path deleted successfully"}
