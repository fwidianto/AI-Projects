"""Database initialization script."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.database import init_db, engine
from src.models.profile import Profile
from src.models.job import JobSource
from src.config.database import SessionLocal

import json


def create_sample_profile():
    """Create a sample profile for testing."""
    db = SessionLocal()
    
    # Check if profile already exists
    existing = db.query(Profile).first()
    if existing:
        print(f"Profile already exists: {existing.name}")
        db.close()
        return
    
    # Create sample profile based on user's background
    profile = Profile(
        name="Fajar Widianto",
        email="fajar@example.com",
        headline="Business Operations Analyst | ERP Specialist",
        summary="Experienced Business Operations Analyst with expertise in ERP systems (SAP ECC, Odoo), cost control, budgeting, and process improvement. Skilled in SQL, data analysis, and business intelligence tools.",
        target_roles=json.dumps([
            "ERP Analyst",
            "Business Analyst",
            "Operations Analyst",
            "Cost Control Analyst",
            "Finance Analyst",
            "Reporting Analyst",
            "Data Analyst",
        ]),
        preferred_locations=json.dumps([
            "Jakarta",
            "Bekasi",
            "Karawang",
            "Remote",
        ]),
        salary_min=15_000_000,
        salary_max=25_000_000,
        experience_years=5,
        education="Bachelor's in Information Systems",
        certifications=json.dumps([
            "SAP ECC Certification",
            "Odoo Implementation",
        ]),
        is_active=True,
        is_default=True,
    )
    
    db.add(profile)
    db.commit()
    
    # Add skills to profile
    from src.models.profile import profile_skills
    
    skills = [
        ("SAP ECC", 5, True),
        ("SAP FI", 4, True),
        ("SAP CO", 4, True),
        ("Odoo ERP", 5, True),
        ("SQL", 4, True),
        ("Excel", 5, True),
        ("Google Sheets", 5, True),
        ("Looker Studio", 4, True),
        ("Power BI", 3, False),
        ("Process Improvement", 4, True),
        ("Cost Control", 5, True),
        ("Budgeting", 5, True),
        ("Financial Analysis", 4, True),
        ("Business Analysis", 5, True),
        ("Requirements Gathering", 4, True),
        ("Data Analysis", 4, True),
        ("ETL", 3, False),
        ("Python", 3, False),
    ]
    
    for skill_name, proficiency, is_key in skills:
        db.execute(
            profile_skills.insert().values(
                profile_id=profile.id,
                skill_name=skill_name,
                proficiency_level=proficiency,
                is_key_skill=is_key,
            )
        )
    
    db.commit()
    print(f"Created sample profile: {profile.name} (ID: {profile.id})")
    
    db.close()


def create_job_sources():
    """Create default job sources."""
    db = SessionLocal()
    
    sources = [
        ("indeed", "Indeed", "https://www.indeed.com", False),
        ("glints", "Glints", "https://glints.com", False),
        ("jobstreet", "JobStreet", "https://www.jobstreet.com", False),
        ("linkedin", "LinkedIn", "https://www.linkedin.com", True),
    ]
    
    for name, display_name, base_url, api_available in sources:
        existing = db.query(JobSource).filter(JobSource.name == name).first()
        if not existing:
            source = JobSource(
                name=name,
                display_name=display_name,
                base_url=base_url,
                api_available=api_available,
            )
            db.add(source)
            print(f"Created job source: {display_name}")
    
    db.commit()
    db.close()


def main():
    """Initialize database and create sample data."""
    print("Initializing database...")
    
    # Create all tables
    init_db()
    print("✓ Database tables created")
    
    # Create job sources
    create_job_sources()
    print("✓ Job sources created")
    
    # Create sample profile
    create_sample_profile()
    print("✓ Sample profile created")
    
    print("\n✅ Database initialization complete!")
    print("\nNext steps:")
    print("1. Run 'streamlit run dashboard/app.py' to start the dashboard")
    print("2. Run 'uvicorn src.api.main:app --reload' to start the API server")


if __name__ == "__main__":
    main()