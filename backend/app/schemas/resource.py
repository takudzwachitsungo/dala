from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ResourceBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    resource_type: str = Field(..., pattern="^(music|reading|exercise|video|article)$")
    category: str = Field(..., pattern="^(anxiety|grief|burnout|depression|relationships|growth|general)$")
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|moderate|challenging)$")
    tags: Optional[List[str]] = []


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    id: UUID
    view_count: int = 0
    helpful_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResourceFilter(BaseModel):
    resource_type: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
