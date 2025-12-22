from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    is_anonymous: bool = False


class PostCreate(PostBase):
    pass


class PostReply(PostBase):
    parent_id: UUID


class PostResponse(PostBase):
    id: UUID
    circle_id: UUID
    user_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    reaction_count: int = 0
    reply_count: int = 0
    is_flagged: bool = False
    is_hidden: bool = False
    created_at: datetime
    
    # Display name handling (anonymous or user)
    author_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PostWithRepliesResponse(PostResponse):
    replies: List[PostResponse] = []
    user_reaction: Optional[str] = None  # User's reaction if any


class PostReactionCreate(BaseModel):
    reaction_type: str = Field(default="relate", pattern="^(relate|support|understood)$")


class PostReactionResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    reaction_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostFlagRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=200)
