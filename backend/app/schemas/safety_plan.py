"""Safety plan schemas"""

from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class SafetyPlanBase(BaseModel):
    """Base safety plan schema"""
    warning_signs: List[str] = []
    internal_coping: List[str] = []
    social_contacts: List[str] = []
    people_to_ask: List[str] = []
    professionals: List[str] = []
    emergency_contacts: List[str] = []
    safe_environment: Optional[str] = None
    reasons_to_live: List[str] = []


class SafetyPlanCreate(SafetyPlanBase):
    """Safety plan creation schema"""
    pass


class SafetyPlanUpdate(SafetyPlanBase):
    """Safety plan update schema"""
    pass


class SafetyPlanResponse(SafetyPlanBase):
    """Safety plan response schema"""
    id: UUID
    user_id: UUID
    
    class Config:
        from_attributes = True
