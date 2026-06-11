"""Profiles API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.config.database import get_db
from src.models.profile import Profile, profile_skills
from src.services.scoring_service import ScoringService
from src.api.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter()


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all profiles."""
    query = db.query(Profile)
    
    if active_only:
        query = query.filter(Profile.is_active == True)
    
    profiles = query.all()
    return [p.to_dict() for p in profiles]


@router.get("/me", response_model=ProfileResponse)
async def get_default_profile(
    db: Session = Depends(get_db),
):
    """Get the default profile."""
    profile = db.query(Profile).filter(Profile.is_default == True).first()
    
    if not profile:
        # Return first profile if no default
        profile = db.query(Profile).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")
    
    return profile.to_dict()


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Get a single profile by ID."""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.to_dict()


@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
):
    """Create a new profile."""
    profile = Profile(
        name=profile_data.name,
        email=profile_data.email,
        headline=profile_data.headline,
        summary=profile_data.summary,
        target_roles=profile_data.target_roles,  # JSON string
        preferred_locations=profile_data.preferred_locations,  # JSON string
        salary_min=profile_data.salary_min,
        salary_max=profile_data.salary_max,
        experience_years=profile_data.experience_years,
        education=profile_data.education,
        certifications=profile_data.certifications,
    )
    
    # Check if this is the first profile (make it default)
    existing_count = db.query(Profile).count()
    if existing_count == 0:
        profile.is_default = True
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Add skills if provided
    if profile_data.skills:
        for skill in profile_data.skills:
            db.execute(
                profile_skills.insert().values(
                    profile_id=profile.id,
                    skill_name=skill["name"],
                    proficiency_level=skill.get("proficiency", 3),
                    is_key_skill=skill.get("is_key", True),
                )
            )
        db.commit()
    
    return profile.to_dict()


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
):
    """Update a profile."""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "skills":
            # Update skills separately
            continue
        if hasattr(profile, field):
            setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile.to_dict()


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Delete a profile."""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Don't allow deleting the last profile
    if db.query(Profile).count() <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last profile")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Profile deleted successfully"}


@router.post("/{profile_id}/set-default")
async def set_default_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Set a profile as the default."""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Clear existing defaults
    db.query(Profile).filter(Profile.is_default == True).update({"is_default": False})
    
    # Set new default
    profile.is_default = True
    db.commit()
    
    return {"message": "Profile set as default"}


@router.post("/{profile_id}/recommendations")
async def generate_recommendations(
    profile_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Generate recommendations for a profile."""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    scoring_service = ScoringService(db)
    recommendations = scoring_service.generate_recommendations(profile_id, limit=limit)
    
    return {
        "count": len(recommendations),
        "recommendations": [r.to_dict() for r in recommendations],
    }