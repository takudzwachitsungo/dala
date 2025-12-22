from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class CircleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., max_length=500)
    icon: Optional[str] = Field(None, max_length=50)


class CircleCreate(CircleBase):
    pass


class CircleResponse(CircleBase):
    id: UUID
    member_count: int = 0
    post_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class CircleMembershipResponse(BaseModel):
    circle_id: UUID
    user_id: UUID
    is_moderator: bool = False
    joined_at: datetime
    
    class Config:
        from_attributes = True


class CircleWithMembershipResponse(CircleResponse):
    is_member: bool = False
    is_moderator: bool = False
