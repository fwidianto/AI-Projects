"""
MVP Configuration Loader

Loads profile and settings from JSON configuration file.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Skill:
    """Skill dataclass."""
    name: str
    proficiency: int = 3  # 1-5 scale
    is_key_skill: bool = False


@dataclass
class SalaryExpectations:
    """Salary expectations dataclass."""
    min: int = 15000000  # 15M IDR
    max: int = 25000000  # 25M IDR
    currency: str = "IDR"


@dataclass
class Profile:
    """User profile dataclass."""
    name: str
    email: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    experience_years: int = 0
    education: Optional[str] = None
    target_roles: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    salary_expectations: SalaryExpectations = field(default_factory=SalaryExpectations)
    
    @property
    def skill_names(self) -> List[str]:
        """Get list of skill names."""
        return [s.name for s in self.skills]
    
    @property
    def key_skill_names(self) -> List[str]:
        """Get list of key skill names."""
        return [s.name for s in self.skills if s.is_key_skill]


@dataclass
class ScoringWeights:
    """Scoring weights dataclass."""
    skills_match: float = 0.40
    title_match: float = 0.30
    location_match: float = 0.15
    salary_match: float = 0.10
    experience_match: float = 0.05


@dataclass
class SearchPreferences:
    """Search preferences dataclass."""
    sources: List[str] = field(default_factory=lambda: ["indeed"])
    default_location: str = "Jakarta"
    max_results_per_search: int = 50
    days_back: int = 30


@dataclass
class Config:
    """Main configuration container."""
    profile: Profile
    scoring_weights: ScoringWeights
    search_preferences: SearchPreferences


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to config file. If None, uses default location.
        
    Returns:
        Config object with all settings
        
    Assumptions:
        - JSON file exists at config_path or default location
        - JSON structure matches expected schema
        - Salary values are in IDR
    """
    if config_path is None:
        # Look for config in multiple locations
        possible_paths = [
            Path("config/profile.json"),
            Path(__file__).parent.parent / "config" / "profile.json",
            Path(os.getcwd()) / "config" / "profile.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
        else:
            raise FileNotFoundError(
                f"Config file not found. Searched: {[str(p) for p in possible_paths]}"
            )
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Parse profile
    profile_data = data.get("profile", {})
    
    skills = []
    for skill_data in profile_data.get("skills", []):
        skills.append(Skill(
            name=skill_data["name"],
            proficiency=skill_data.get("proficiency", 3),
            is_key_skill=skill_data.get("is_key_skill", False),
        ))
    
    salary_data = profile_data.get("salary_expectations", {})
    salary = SalaryExpectations(
        min=salary_data.get("min", 15000000),
        max=salary_data.get("max", 25000000),
        currency=salary_data.get("currency", "IDR"),
    )
    
    profile = Profile(
        name=profile_data.get("name", "Unknown"),
        email=profile_data.get("email"),
        headline=profile_data.get("headline"),
        summary=profile_data.get("summary"),
        experience_years=profile_data.get("experience_years", 0),
        education=profile_data.get("education"),
        target_roles=profile_data.get("target_roles", []),
        preferred_locations=profile_data.get("preferred_locations", []),
        skills=skills,
        certifications=profile_data.get("certifications", []),
        salary_expectations=salary,
    )
    
    # Parse scoring weights
    weights_data = data.get("scoring_weights", {})
    scoring_weights = ScoringWeights(
        skills_match=weights_data.get("skills_match", 0.40),
        title_match=weights_data.get("title_match", 0.30),
        location_match=weights_data.get("location_match", 0.15),
        salary_match=weights_data.get("salary_match", 0.10),
        experience_match=weights_data.get("experience_match", 0.05),
    )
    
    # Parse search preferences
    search_data = data.get("search_preferences", {})
    search_preferences = SearchPreferences(
        sources=search_data.get("sources", ["indeed"]),
        default_location=search_data.get("default_location", "Jakarta"),
        max_results_per_search=search_data.get("max_results_per_search", 50),
        days_back=search_data.get("days_back", 30),
    )
    
    return Config(
        profile=profile,
        scoring_weights=scoring_weights,
        search_preferences=search_preferences,
    )


def save_sample_config(output_path: str = "config/profile.json") -> None:
    """Save a sample configuration file."""
    sample_config = {
        "profile": {
            "name": "Your Name",
            "email": "your.email@example.com",
            "headline": "Your Professional Headline",
            "summary": "Brief professional summary",
            "experience_years": 5,
            "education": "Your Degree",
            "target_roles": ["Job Title 1", "Job Title 2"],
            "preferred_locations": ["Jakarta", "Remote"],
            "salary_expectations": {
                "min": 15000000,
                "max": 25000000,
                "currency": "IDR"
            },
            "skills": [
                {"name": "Skill Name", "proficiency": 4, "is_key_skill": True}
            ],
            "certifications": ["Certification 1"]
        },
        "search_preferences": {
            "sources": ["indeed"],
            "default_location": "Jakarta",
            "max_results_per_search": 50,
            "days_back": 30
        },
        "scoring_weights": {
            "skills_match": 0.40,
            "title_match": 0.30,
            "location_match": 0.15,
            "salary_match": 0.10,
            "experience_match": 0.05
        }
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"Sample config saved to: {output_path}")