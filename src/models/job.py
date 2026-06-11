"""Job posting model."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.config.database import Base


class JobSource(Base):
    """Job board source model."""

    __tablename__ = "job_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_available: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="source")

    def __repr__(self) -> str:
        return f"<JobSource(name='{self.name}')>"


class Job(Base):
    """Job posting model."""

    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "source", name="uq_job_source_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Source information
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[int] = mapped_column(Integer, ForeignKey("job_sources.id"), nullable=False)

    # Job details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)

    # Salary (in IDR)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), default="IDR")
    salary_display: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Job type
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Full-time, Contract, etc.

    # Description and requirements
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    benefits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # URLs
    apply_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Dates
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False)

    # Application tracking
    application_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    application_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    source_obj: Mapped["JobSource"] = relationship("JobSource", back_populates="jobs")
    skills: Mapped[List["JobSkill"]] = relationship(
        "JobSkill", back_populates="job", cascade="all, delete-orphan"
    )
    scores: Mapped[List["JobScore"]] = relationship(
        "JobScore", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"

    @property
    def skills_list(self) -> List[str]:
        """Get extracted skills as a list."""
        return [skill.skill_name for skill in self.skills]

    @property
    def salary_range_display(self) -> str:
        """Get formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min/1_000_000:.0f}M - {self.salary_max/1_000_000:.0f}M IDR"
        elif self.salary_min:
            return f"{self.salary_min/1_000_000:.0f}M+ IDR"
        elif self.salary_display:
            return self.salary_display
        return "Salary not disclosed"

    @property
    def age_display(self) -> str:
        """Get job age as a human-readable string."""
        if not self.posted_date:
            return "Unknown"
        
        from datetime import timedelta
        age = datetime.utcnow() - self.posted_date
        
        if age < timedelta(days=1):
            hours = int(age.total_seconds() / 3600)
            return f"{hours}h ago" if hours > 0 else "Just posted"
        elif age < timedelta(days=7):
            days = age.days
            return f"{days}d ago"
        elif age < timedelta(days=30):
            weeks = age.days // 7
            return f"{weeks}w ago"
        else:
            months = age.days // 30
            return f"{months}mo ago"

    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "is_remote": self.is_remote,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_display": self.salary_range_display,
            "employment_type": self.employment_type,
            "description": self.description,
            "requirements": self.requirements,
            "benefits": self.benefits,
            "apply_url": self.apply_url,
            "source_url": self.source_url,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "is_active": self.is_active,
            "is_applied": self.is_applied,
            "skills": self.skills_list,
            "age_display": self.age_display,
        }


class JobSkill(Base):
    """Extracted skills from job postings."""

    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(default=1.0)  # 0.0 - 1.0
    is_extracted: Mapped[bool] = mapped_column(Boolean, default=True)  # True=ML extracted, False=manual

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="skills")

    def __repr__(self) -> str:
        return f"<JobSkill(skill='{self.skill_name}', confidence={self.confidence})>"


# Import at bottom to avoid circular imports
from src.models.score import JobScore