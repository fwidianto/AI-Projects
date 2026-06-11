"""Job-related Pydantic schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class JobResponse(BaseModel):
    """Schema for job response."""
    
    id: int
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_display: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    apply_url: Optional[str] = None
    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    is_active: bool = True
    is_applied: bool = False
    skills: List[str] = []
    age_display: Optional[str] = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Schema for paginated job list."""
    
    items: List[JobResponse]
    total: int
    limit: int = 100
    offset: int = 0


class JobSearchParams(BaseModel):
    """Schema for job search parameters."""
    
    query: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    sources: Optional[List[str]] = None
    days_back: Optional[int] = None
    limit: int = Field(default=100, ge=1, le=500)


class JobCreate(BaseModel):
    """Schema for creating a job."""
    
    source: str
    source_id: str
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "IDR"
    salary_display: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    apply_url: Optional[str] = None
    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None


class JobScoreResponse(BaseModel):
    """Schema for job score response."""
    
    id: int
    profile_id: int
    job_id: int
    total_score: float
    skills_score: float
    title_score: float
    location_score: float
    salary_score: float
    experience_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    score_label: str
    scored_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class JobWithScore(BaseModel):
    """Schema for job with score."""
    
    job: JobResponse
    score: JobScoreResponse