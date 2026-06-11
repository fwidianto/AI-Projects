"""Job score and recommendation models."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.config.database import Base


class JobScore(Base):
    """Job match score model."""

    __tablename__ = "job_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    # Overall score (0-100)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Component scores (0-100)
    skills_score: Mapped[float] = mapped_column(Float, default=0.0)
    title_score: Mapped[float] = mapped_column(Float, default=0.0)
    location_score: Mapped[float] = mapped_column(Float, default=0.0)
    salary_score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Matched skills (JSON)
    matched_skills: Mapped[str] = mapped_column(Text, default="[]")
    missing_skills: Mapped[str] = mapped_column(Text, default="[]")

    # Metadata
    scoring_method: Mapped[str] = mapped_column(String(50), default="embedding")  # embedding, keyword, hybrid
    scored_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="scores")
    job: Mapped["Job"] = relationship("Job", back_populates="scores")

    def __repr__(self) -> str:
        return f"<JobScore(profile={self.profile_id}, job={self.job_id}, score={self.total_score:.1f})>"

    @property
    def matched_skills_list(self) -> List[str]:
        """Get matched skills as a list."""
        import json
        try:
            return json.loads(self.matched_skills) if self.matched_skills else []
        except json.JSONDecodeError:
            return []

    @property
    def missing_skills_list(self) -> List[str]:
        """Get missing skills as a list."""
        import json
        try:
            return json.loads(self.missing_skills) if self.missing_skills else []
        except json.JSONDecodeError:
            return []

    @property
    def score_label(self) -> str:
        """Get human-readable score label."""
        if self.total_score >= 90:
            return "Excellent Match"
        elif self.total_score >= 75:
            return "Strong Match"
        elif self.total_score >= 60:
            return "Good Match"
        elif self.total_score >= 40:
            return "Moderate Match"
        else:
            return "Low Match"

    @property
    def score_color(self) -> str:
        """Get color code for score."""
        if self.total_score >= 90:
            return "#28a745"  # Green
        elif self.total_score >= 75:
            return "#17a2b8"  # Cyan
        elif self.total_score >= 60:
            return "#ffc107"  # Yellow
        elif self.total_score >= 40:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red

    def to_dict(self) -> dict:
        """Convert score to dictionary."""
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "job_id": self.job_id,
            "total_score": round(self.total_score, 1),
            "skills_score": round(self.skills_score, 1),
            "title_score": round(self.title_score, 1),
            "location_score": round(self.location_score, 1),
            "salary_score": round(self.salary_score, 1),
            "experience_score": round(self.experience_score, 1),
            "matched_skills": self.matched_skills_list,
            "missing_skills": self.missing_skills_list,
            "score_label": self.score_label,
            "scored_at": self.scored_at.isoformat() if self.scored_at else None,
        }


class Recommendation(Base):
    """Job recommendations model."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    # Recommendation details
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # apply, research, watch
    priority: Mapped[int] = mapped_column(Integer, default=3)  # 1=High, 2=Medium, 3=Low
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_items: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array

    # Status tracking
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    action_taken: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation(type='{self.recommendation_type}', priority={self.priority})>"

    @property
    def action_items_list(self) -> List[str]:
        """Get action items as a list."""
        import json
        try:
            return json.loads(self.action_items) if self.action_items else []
        except json.JSONDecodeError:
            return []

    @property
    def priority_label(self) -> str:
        """Get human-readable priority label."""
        labels = {1: "High Priority", 2: "Medium Priority", 3: "Low Priority"}
        return labels.get(self.priority, "Unknown")

    def to_dict(self) -> dict:
        """Convert recommendation to dictionary."""
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "job_id": self.job_id,
            "recommendation_type": self.recommendation_type,
            "priority": self.priority,
            "priority_label": self.priority_label,
            "reason": self.reason,
            "action_items": self.action_items_list,
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
            "action_taken": self.action_taken,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Import at top to avoid circular imports (models already defined)
from src.models.profile import Profile
from src.models.job import Job