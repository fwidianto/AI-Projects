"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "headline": "Software Engineer",
        "target_roles": '["Software Engineer", "Data Analyst"]',
        "preferred_locations": '["Jakarta", "Remote"]',
        "salary_min": 15000000,
        "salary_max": 25000000,
        "experience_years": 5,
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "source": "indeed",
        "source_id": "test-123",
        "title": "ERP Analyst",
        "company": "Test Company",
        "location": "Jakarta",
        "is_remote": False,
        "salary_min": 20000000,
        "salary_max": 25000000,
        "description": "Looking for an ERP Analyst with SAP experience",
    }