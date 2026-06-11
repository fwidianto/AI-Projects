"""Job service for job operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session, joinedload

from src.models.job import Job, JobSource, JobSkill
from src.models.profile import Profile
from src.models.score import JobScore
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JobService:
    """Service for job-related operations."""

    def __init__(self, db: Session):
        """Initialize job service with database session."""
        self.db = db

    # =============================================================================
    # Job CRUD Operations
    # =============================================================================

    def create_job(self, job_data: Dict[str, Any]) -> Job:
        """
        Create a new job posting.
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            Job: Created job instance
        """
        # Get or create job source
        source_name = job_data.get("source", "unknown")
        source = self.get_or_create_source(source_name)
        
        # Create job
        job = Job(
            source_id=job_data.get("source_id", ""),
            source=source.id,
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            location=job_data.get("location"),
            is_remote=job_data.get("is_remote", False),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            salary_currency=job_data.get("salary_currency", "IDR"),
            salary_display=job_data.get("salary_display"),
            employment_type=job_data.get("employment_type"),
            description=job_data.get("description"),
            requirements=job_data.get("requirements"),
            benefits=job_data.get("benefits"),
            apply_url=job_data.get("apply_url"),
            source_url=job_data.get("source_url"),
            posted_date=job_data.get("posted_date"),
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Created job: {job.title} at {job.company}")
        return job

    def get_job(self, job_id: int) -> Optional[Job]:
        """Get job by ID."""
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_job_by_source(self, source: str, source_id: str) -> Optional[Job]:
        """Get job by source and source_id."""
        source_obj = self.get_source_by_name(source)
        if not source_obj:
            return None
        
        return (
            self.db.query(Job)
            .filter(and_(Job.source == source_obj.id, Job.source_id == source_id))
            .first()
        )

    def get_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = True,
        source: Optional[str] = None,
    ) -> List[Job]:
        """
        Get list of jobs.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            active_only: Only return active jobs
            source: Filter by source name
            
        Returns:
            List of Job instances
        """
        query = self.db.query(Job).options(joinedload(Job.source_obj))
        
        if active_only:
            query = query.filter(Job.is_active == True)
        
        if source:
            source_obj = self.get_source_by_name(source)
            if source_obj:
                query = query.filter(Job.source == source_obj.id)
        
        return (
            query.order_by(desc(Job.scraped_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_job(self, job_id: int, job_data: Dict[str, Any]) -> Optional[Job]:
        """Update job data."""
        job = self.get_job(job_id)
        if not job:
            return None
        
        for key, value in job_data.items():
            if hasattr(job, key) and key not in ["id", "source"]:
                setattr(job, key, value)
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Updated job {job_id}")
        return job

    def delete_job(self, job_id: int) -> bool:
        """Delete a job."""
        job = self.get_job(job_id)
        if not job:
            return False
        
        self.db.delete(job)
        self.db.commit()
        
        logger.info(f"Deleted job {job_id}")
        return True

    # =============================================================================
    # Job Source Operations
    # =============================================================================

    def get_or_create_source(self, name: str) -> JobSource:
        """Get or create a job source."""
        source = self.get_source_by_name(name)
        if source:
            return source
        
        source = JobSource(
            name=name.lower(),
            display_name=name,
            base_url=f"https://www.{name.lower()}.com",
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        
        return source

    def get_source_by_name(self, name: str) -> Optional[JobSource]:
        """Get job source by name."""
        return self.db.query(JobSource).filter(JobSource.name == name.lower()).first()

    def get_all_sources(self) -> List[JobSource]:
        """Get all job sources."""
        return self.db.query(JobSource).all()

    # =============================================================================
    # Job Skills Operations
    # =============================================================================

    def add_job_skill(self, job_id: int, skill_name: str, confidence: float = 1.0) -> JobSkill:
        """Add a skill to a job."""
        # Check if skill already exists
        existing = (
            self.db.query(JobSkill)
            .filter(and_(JobSkill.job_id == job_id, JobSkill.skill_name == skill_name))
            .first()
        )
        
        if existing:
            existing.confidence = confidence
            self.db.commit()
            return existing
        
        skill = JobSkill(job_id=job_id, skill_name=skill_name, confidence=confidence)
        self.db.add(skill)
        self.db.commit()
        
        return skill

    def set_job_skills(self, job_id: int, skills: List[Dict[str, Any]]) -> None:
        """Set job skills (replace existing)."""
        # Remove existing skills
        self.db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()
        
        # Add new skills
        for skill_data in skills:
            self.add_job_skill(
                job_id,
                skill_data.get("name", ""),
                skill_data.get("confidence", 1.0),
            )

    def get_job_skills(self, job_id: int) -> List[str]:
        """Get skills for a job."""
        skills = self.db.query(JobSkill).filter(JobSkill.job_id == job_id).all()
        return [s.skill_name for s in skills]

    # =============================================================================
    # Search Operations
    # =============================================================================

    def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        sources: Optional[List[str]] = None,
        days_back: Optional[int] = None,
        limit: int = 100,
    ) -> List[Job]:
        """
        Search jobs with filters.
        
        Args:
            query: Search query (title, company, description)
            location: Location filter
            salary_min: Minimum salary
            salary_max: Maximum salary
            sources: List of source names to include
            days_back: Only show jobs from last N days
            limit: Maximum results
            
        Returns:
            List of matching jobs
        """
        db_query = self.db.query(Job).options(joinedload(Job.source_obj))
        
        # Text search
        if query:
            search_filter = or_(
                Job.title.ilike(f"%{query}%"),
                Job.company.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%"),
            )
            db_query = db_query.filter(search_filter)
        
        # Location filter
        if location:
            db_query = db_query.filter(
                or_(
                    Job.location.ilike(f"%{location}%"),
                    Job.is_remote == True,
                )
            )
        
        # Salary filters
        if salary_min:
            db_query = db_query.filter(or_(Job.salary_min >= salary_min, Job.salary_min.is_(None)))
        if salary_max:
            db_query = db_query.filter(or_(Job.salary_max <= salary_max, Job.salary_max.is_(None)))
        
        # Source filter
        if sources:
            source_ids = []
            for source_name in sources:
                source = self.get_source_by_name(source_name)
                if source:
                    source_ids.append(source.id)
            if source_ids:
                db_query = db_query.filter(Job.source.in_(source_ids))
        
        # Date filter
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            db_query = db_query.filter(Job.posted_date >= cutoff_date)
        
        # Only active jobs
        db_query = db_query.filter(Job.is_active == True)
        
        return db_query.order_by(desc(Job.scraped_at)).limit(limit).all()

    # =============================================================================
    # Statistics
    # =============================================================================

    def get_job_stats(self) -> Dict[str, Any]:
        """Get job statistics."""
        total_jobs = self.db.query(Job).count()
        active_jobs = self.db.query(Job).filter(Job.is_active == True).count()
        applied_jobs = self.db.query(Job).filter(Job.is_applied == True).count()
        
        # Jobs by source
        source_stats = []
        sources = self.get_all_sources()
        for source in sources:
            count = self.db.query(Job).filter(Job.source == source.id).count()
            source_stats.append({"name": source.display_name, "count": count})
        
        # Recent jobs (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = self.db.query(Job).filter(Job.scraped_at >= week_ago).count()
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "applied_jobs": applied_jobs,
            "recent_jobs_7d": recent_count,
            "by_source": source_stats,
        }

    # =============================================================================
    # Bulk Operations
    # =============================================================================

    def bulk_create_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[Job]:
        """Create multiple jobs at once."""
        created_jobs = []
        
        for job_data in jobs_data:
            # Check for duplicates
            existing = self.get_job_by_source(
                job_data.get("source", ""),
                job_data.get("source_id", ""),
            )
            
            if existing:
                # Update existing
                updated = self.update_job(existing.id, job_data)
                if updated:
                    created_jobs.append(updated)
            else:
                # Create new
                job = self.create_job(job_data)
                created_jobs.append(job)
        
        return created_jobs

    def mark_jobs_as_applied(self, job_ids: List[int]) -> int:
        """Mark multiple jobs as applied."""
        count = (
            self.db.query(Job)
            .filter(Job.id.in_(job_ids))
            .update(
                {"is_applied": True, "application_date": datetime.utcnow()},
                synchronize_session=False,
            )
        )
        self.db.commit()
        return count

    def deactivate_old_jobs(self, days: int = 90) -> int:
        """Deactivate jobs older than N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = (
            self.db.query(Job)
            .filter(
                and_(
                    Job.scraped_at < cutoff_date,
                    Job.is_applied == False,
                    Job.is_active == True,
                )
            )
            .update({"is_active": False}, synchronize_session=False)
        )
        self.db.commit()
        return count