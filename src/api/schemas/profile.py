"""Profile-related Pydantic schemas."""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class SkillInput(BaseModel):
    """Schema for skill input."""
    
    name: str = Field(..., min_length=1, max_length=100)
    proficiency: int = Field(default=3, ge=1, le=5)
    is_key: bool = True


class ProfileCreate(BaseModel):
    """Schema for creating a profile."""
    
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    target_roles: str = Field(default="[]")  # JSON string
    preferred_locations: str = Field(default="[]")  # JSON string
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0)
    education: Optional[str] = None
    certifications: Optional[str] = None
    skills: Optional[List[SkillInput]] = None


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    target_roles: Optional[str] = None
    preferred_locations: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0)
    education: Optional[str] = None
    certifications: Optional[str] = None
    is_active: Optional[bool] = None
    skills: Optional[List[SkillInput]] = None


class ProfileResponse(BaseModel):
    """Schema for profile response."""
    
    id: int
    name: str
    email: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    target_roles: List[str] = []
    preferred_locations: List[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""
    
    id: int
    profile_id: int
    job_id: int
    recommendation_type: str
    priority: int
    priority_label: str
    reason: Optional[str] = None
    action_items: List[str] = []
    is_read: bool = False
    is_dismissed: bool = False
    action_taken: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}