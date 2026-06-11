"""Tests for job service."""

import pytest
from src.services.job_service import JobService
from src.models.profile import Profile
from src.models.job import Job, JobSource


class TestJobService:
    """Test cases for JobService."""

    def test_create_job(self, db_session, sample_job_data):
        """Test creating a job."""
        service = JobService(db_session)
        
        job = service.create_job(sample_job_data)
        
        assert job.id is not None
        assert job.title == sample_job_data["title"]
        assert job.company == sample_job_data["company"]
        assert job.is_active is True

    def test_get_job(self, db_session, sample_job_data):
        """Test getting a job by ID."""
        service = JobService(db_session)
        
        created_job = service.create_job(sample_job_data)
        retrieved_job = service.get_job(created_job.id)
        
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id

    def test_get_jobs(self, db_session, sample_job_data):
        """Test listing jobs."""
        service = JobService(db_session)
        
        # Create multiple jobs
        service.create_job(sample_job_data)
        sample_job_data["source_id"] = "test-456"
        service.create_job(sample_job_data)
        
        jobs = service.get_jobs(limit=10)
        
        assert len(jobs) == 2

    def test_search_jobs(self, db_session, sample_job_data):
        """Test searching jobs."""
        service = JobService(db_session)
        
        service.create_job(sample_job_data)
        
        results = service.search_jobs(query="ERP")
        
        assert len(results) >= 1

    def test_get_job_stats(self, db_session, sample_job_data):
        """Test getting job statistics."""
        service = JobService(db_session)
        
        service.create_job(sample_job_data)
        
        stats = service.get_job_stats()
        
        assert "total_jobs" in stats
        assert stats["total_jobs"] >= 1