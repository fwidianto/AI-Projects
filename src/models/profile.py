"""User profile model."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.config.database import Base


# Association table for profile skills
profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
    Column("skill_name", String(100), nullable=False),
    Column("proficiency_level", Integer, default=3),  # 1-5 scale
    Column("is_key_skill", Boolean, default=True),
)


class Profile(Base):
    """User professional profile model."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Target roles (JSON array stored as text)
    target_roles: Mapped[str] = mapped_column(Text, default="[]")
    preferred_locations: Mapped[str] = mapped_column(Text, default="[]")

    # Salary expectations
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Experience
    experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Education & Certifications
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    certifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    scores: Mapped[List["JobScore"]] = relationship(
        "JobScore", back_populates="profile", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, name='{self.name}')>"

    @property
    def target_roles_list(self) -> List[str]:
        """Get target roles as a list."""
        import json
        try:
            return json.loads(self.target_roles) if self.target_roles else []
        except json.JSONDecodeError:
            return []

    @target_roles_list.setter
    def target_roles_list(self, roles: List[str]) -> None:
        """Set target roles from a list."""
        import json
        self.target_roles = json.dumps(roles)

    @property
    def locations_list(self) -> List[str]:
        """Get preferred locations as a list."""
        import json
        try:
            return json.loads(self.preferred_locations) if self.preferred_locations else []
        except json.JSONDecodeError:
            return []

    @locations_list.setter
    def locations_list(self, locations: List[str]) -> None:
        """Set preferred locations from a list."""
        import json
        self.preferred_locations = json.dumps(locations)

    @property
    def skills_list(self) -> List[str]:
        """Get skills from association table."""
        # This would be populated from profile_skills table
        return []

    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "headline": self.headline,
            "summary": self.summary,
            "target_roles": self.target_roles_list,
            "preferred_locations": self.locations_list,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "experience_years": self.experience_years,
            "education": self.education,
            "certifications": self.certifications,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Import at bottom to avoid circular imports
from src.models.score import JobScore, Recommendation