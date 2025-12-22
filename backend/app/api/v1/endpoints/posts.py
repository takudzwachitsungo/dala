from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.post import Post, PostReaction
from app.db.models.circle import Circle, CircleMembership
from app.schemas.post import (
    PostCreate,
    PostReply,
    PostResponse,
    PostWithRepliesResponse,
    PostReactionCreate,
    PostFlagRequest
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/circles/{circle_id}/posts", response_model=List[PostWithRepliesResponse])
async def list_circle_posts(
    circle_id: UUID,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List posts in a circle (requires membership)"""
    # Check membership
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a member to view posts"
        )
    
    # Get posts (top-level only, not replies)
    result = await db.execute(
        select(Post)
        .where(
            and_(
                Post.circle_id == circle_id,
                Post.parent_id.is_(None),
                Post.is_hidden == False
            )
        )
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = result.scalars().all()
    
    # Get user's reactions
    post_ids = [p.id for p in posts]
    reactions_result = await db.execute(
        select(PostReaction).where(
            and_(
                PostReaction.post_id.in_(post_ids),
                PostReaction.user_id == current_user.id
            )
        )
    )
    user_reactions = {r.post_id: r.reaction_type for r in reactions_result.scalars().all()}
    
    # Get replies for each post
    replies_result = await db.execute(
        select(Post).where(
            and_(
                Post.parent_id.in_(post_ids),
                Post.is_hidden == False
            )
        )
        .order_by(Post.created_at)
    )
    all_replies = replies_result.scalars().all()
    
    # Group replies by parent
    replies_by_parent = {}
    for reply in all_replies:
        if reply.parent_id not in replies_by_parent:
            replies_by_parent[reply.parent_id] = []
        replies_by_parent[reply.parent_id].append(reply)
    
    # Build response
    response = []
    for post in posts:
        post_dict = PostResponse.model_validate(post).model_dump()
        post_dict["author_name"] = "Anonymous" if post.is_anonymous else f"User {post.user_id}"
        
        # Add replies
        replies = []
        for reply in replies_by_parent.get(post.id, []):
            reply_dict = PostResponse.model_validate(reply).model_dump()
            reply_dict["author_name"] = "Anonymous" if reply.is_anonymous else f"User {reply.user_id}"
            replies.append(PostResponse(**reply_dict))
        
        post_dict["replies"] = replies
        post_dict["user_reaction"] = user_reactions.get(post.id)
        response.append(PostWithRepliesResponse(**post_dict))
    
    return response


@router.post("/circles/{circle_id}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    circle_id: UUID,
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a post in a circle (requires membership)"""
    # Check membership
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a member to post"
        )
    
    # Create post
    post = Post(
        circle_id=circle_id,
        user_id=current_user.id,
        content=post_data.content,
        is_anonymous=post_data.is_anonymous
    )
    db.add(post)
    
    # Update circle post count
    circle_result = await db.execute(select(Circle).where(Circle.id == circle_id))
    circle = circle_result.scalar_one()
    circle.post_count += 1
    
    await db.commit()
    await db.refresh(post)
    
    response_dict = PostResponse.model_validate(post).model_dump()
    response_dict["author_name"] = "Anonymous" if post.is_anonymous else f"User {post.user_id}"
    return PostResponse(**response_dict)


@router.post("/posts/{post_id}/reply", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_post(
    post_id: UUID,
    reply_data: PostReply,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reply to a post"""
    # Get parent post
    parent_result = await db.execute(select(Post).where(Post.id == post_id))
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check membership in circle
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == parent.circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a member to reply"
        )
    
    # Create reply
    reply = Post(
        circle_id=parent.circle_id,
        user_id=current_user.id,
        parent_id=post_id,
        content=reply_data.content,
        is_anonymous=reply_data.is_anonymous
    )
    db.add(reply)
    
    # Update parent reply count
    parent.reply_count += 1
    
    await db.commit()
    await db.refresh(reply)
    
    response_dict = PostResponse.model_validate(reply).model_dump()
    response_dict["author_name"] = "Anonymous" if reply.is_anonymous else f"User {reply.user_id}"
    return PostResponse(**response_dict)


@router.post("/posts/{post_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
async def add_reaction(
    post_id: UUID,
    reaction_data: PostReactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add or update reaction to a post"""
    # Get post
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check membership
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == post.circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a member to react"
        )
    
    # Check if reaction exists
    reaction_result = await db.execute(
        select(PostReaction).where(
            and_(
                PostReaction.post_id == post_id,
                PostReaction.user_id == current_user.id
            )
        )
    )
    existing = reaction_result.scalar_one_or_none()
    
    if existing:
        # Update reaction type
        if existing.reaction_type != reaction_data.reaction_type:
            existing.reaction_type = reaction_data.reaction_type
    else:
        # Create new reaction
        reaction = PostReaction(
            post_id=post_id,
            user_id=current_user.id,
            reaction_type=reaction_data.reaction_type
        )
        db.add(reaction)
        post.reaction_count += 1
    
    await db.commit()


@router.delete("/posts/{post_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove reaction from a post"""
    # Get reaction
    result = await db.execute(
        select(PostReaction).where(
            and_(
                PostReaction.post_id == post_id,
                PostReaction.user_id == current_user.id
            )
        )
    )
    reaction = result.scalar_one_or_none()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    # Update post count
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one()
    post.reaction_count = max(0, post.reaction_count - 1)
    
    await db.delete(reaction)
    await db.commit()


@router.post("/posts/{post_id}/flag", status_code=status.HTTP_204_NO_CONTENT)
async def flag_post(
    post_id: UUID,
    flag_data: PostFlagRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Flag a post for moderation"""
    # Get post
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check membership
    membership_result = await db.execute(
        select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == post.circle_id,
                CircleMembership.user_id == current_user.id
            )
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a member to flag posts"
        )
    
    # Flag post
    post.is_flagged = True
    post.flag_reason = flag_data.reason
    await db.commit()
