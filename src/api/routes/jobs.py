"""Jobs API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.config.database import get_db
from src.services.job_service import JobService
from src.services.scoring_service import ScoringService
from src.api.schemas.job import JobResponse, JobListResponse, JobSearchParams

router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all jobs with optional filters."""
    service = JobService(db)
    jobs = service.get_jobs(limit=limit, offset=offset, active_only=active_only, source=source)
    
    return {
        "items": [job.to_dict() for job in jobs],
        "total": len(jobs),
        "limit": limit,
        "offset": offset,
    }


@router.get("/search")
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None),
    salary_max: Optional[int] = Query(None),
    sources: Optional[List[str]] = Query(None),
    days_back: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Search jobs with filters."""
    service = JobService(db)
    jobs = service.search_jobs(
        query=q,
        location=location,
        salary_min=salary_min,
        salary_max=salary_max,
        sources=sources,
        days_back=days_back,
        limit=limit,
    )
    
    return {
        "items": [job.to_dict() for job in jobs],
        "total": len(jobs),
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    """Get a single job by ID."""
    service = JobService(db)
    job = service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()


@router.post("/")
async def create_job(
    job_data: dict,
    db: Session = Depends(get_db),
):
    """Create a new job."""
    service = JobService(db)
    
    try:
        job = service.create_job(job_data)
        return {"id": job.id, "message": "Job created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{job_id}")
async def update_job(
    job_id: int,
    job_data: dict,
    db: Session = Depends(get_db),
):
    """Update a job."""
    service = JobService(db)
    
    job = service.update_job(job_id, job_data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"id": job.id, "message": "Job updated successfully"}


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    """Delete a job."""
    service = JobService(db)
    
    if not service.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


@router.get("/stats/summary")
async def get_job_stats(
    db: Session = Depends(get_db),
):
    """Get job statistics."""
    service = JobService(db)
    return service.get_job_stats()


@router.post("/{job_id}/score")
async def score_job(
    job_id: int,
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Score a job for a profile."""
    scoring_service = ScoringService(db)
    
    try:
        score = scoring_service.score_job(job_id, profile_id)
        return score.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/score-all")
async def score_all_jobs(
    profile_id: int,
    min_score: float = Query(0, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Score all jobs for a profile."""
    scoring_service = ScoringService(db)
    scores = scoring_service.score_all_jobs(profile_id, min_score=min_score)
    
    return {
        "scored_count": len(scores),
        "scores": [s.to_dict() for s in scores],
    }


@router.get("/top-matches")
async def get_top_matches(
    profile_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Get top matching jobs for a profile."""
    scoring_service = ScoringService(db)
    matches = scoring_service.get_top_jobs(profile_id, limit=limit, min_score=min_score)
    
    return {"items": matches, "count": len(matches)}