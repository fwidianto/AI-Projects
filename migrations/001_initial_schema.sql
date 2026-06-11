-- =============================================================================
-- AI Job Intelligence Platform - Initial Schema
-- =============================================================================

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- Job Sources Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS job_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    logo_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    api_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default sources
INSERT INTO job_sources (name, display_name, base_url, api_available) VALUES
    ('indeed', 'Indeed', 'https://www.indeed.com', FALSE),
    ('glints', 'Glints', 'https://glints.com', FALSE),
    ('jobstreet', 'JobStreet', 'https://www.jobstreet.com', FALSE),
    ('linkedin', 'LinkedIn', 'https://www.linkedin.com', TRUE)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- Profiles Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    headline VARCHAR(255),
    summary TEXT,
    target_roles TEXT DEFAULT '[]',  -- JSON array
    preferred_locations TEXT DEFAULT '[]',  -- JSON array
    salary_min INTEGER,
    salary_max INTEGER,
    experience_years INTEGER,
    education TEXT,
    certifications TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Profile Skills Table (Association)
-- =============================================================================

CREATE TABLE IF NOT EXISTS profile_skills (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level INTEGER DEFAULT 3 CHECK (proficiency_level BETWEEN 1 AND 5),
    is_key_skill BOOLEAN DEFAULT TRUE,
    UNIQUE(profile_id, skill_name)
);

CREATE INDEX idx_profile_skills_profile ON profile_skills(profile_id);
CREATE INDEX idx_profile_skills_skill ON profile_skills(skill_name);

-- =============================================================================
-- Jobs Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100) NOT NULL,
    source INTEGER NOT NULL REFERENCES job_sources(id),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    is_remote BOOLEAN DEFAULT FALSE,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'IDR',
    salary_display VARCHAR(100),
    employment_type VARCHAR(50),
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    apply_url VARCHAR(500),
    source_url VARCHAR(500),
    posted_date TIMESTAMP,
    expires_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    application_date TIMESTAMP,
    application_status VARCHAR(50),
    interview_date TIMESTAMP,
    notes TEXT,
    UNIQUE(source_id, source)
);

-- Indexes for performance
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_posted ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_scraped ON jobs(scraped_at DESC);
CREATE INDEX idx_jobs_is_active ON jobs(is_active);
CREATE INDEX idx_jobs_is_applied ON jobs(is_applied);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_title ON jobs(title);

-- =============================================================================
-- Job Skills Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS job_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    confidence FLOAT DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
    is_extracted BOOLEAN DEFAULT TRUE,
    UNIQUE(job_id, skill_name)
);

CREATE INDEX idx_job_skills_job ON job_skills(job_id);
CREATE INDEX idx_job_skills_skill ON job_skills(skill_name);

-- =============================================================================
-- Job Scores Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS job_scores (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    total_score FLOAT DEFAULT 0 CHECK (total_score BETWEEN 0 AND 100),
    skills_score FLOAT DEFAULT 0,
    title_score FLOAT DEFAULT 0,
    location_score FLOAT DEFAULT 0,
    salary_score FLOAT DEFAULT 0,
    experience_score FLOAT DEFAULT 0,
    matched_skills TEXT DEFAULT '[]',  -- JSON array
    missing_skills TEXT DEFAULT '[]',  -- JSON array
    scoring_method VARCHAR(50) DEFAULT 'weighted',
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_id, job_id)
);

CREATE INDEX idx_job_scores_profile ON job_scores(profile_id);
CREATE INDEX idx_job_scores_job ON job_scores(job_id);
CREATE INDEX idx_job_scores_total ON job_scores(total_score DESC);

-- =============================================================================
-- Recommendations Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL,  -- apply, research, watch
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 3),  -- 1=High, 2=Medium, 3=Low
    reason TEXT,
    action_items TEXT,  -- JSON array
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    action_taken VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendations_profile ON recommendations(profile_id);
CREATE INDEX idx_recommendations_job ON recommendations(job_id);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);
CREATE INDEX idx_recommendations_created ON recommendations(created_at DESC);

-- =============================================================================
-- Full-Text Search Index (Optional, for PostgreSQL)
-- =============================================================================

-- Create GIN index for full-text search on jobs
CREATE INDEX idx_jobs_fulltext ON jobs USING GIN (
    to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(company, '') || ' ' || COALESCE(description, ''))
);

-- =============================================================================
-- Triggers
-- =============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at
    BEFORE UPDATE ON recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Comments
-- =============================================================================

COMMENT ON TABLE profiles IS 'User professional profiles for job matching';
COMMENT ON TABLE jobs IS 'Job postings from various sources';
COMMENT ON TABLE job_scores IS 'Job match scores calculated for each profile';
COMMENT ON TABLE recommendations IS 'Actionable job recommendations for users';