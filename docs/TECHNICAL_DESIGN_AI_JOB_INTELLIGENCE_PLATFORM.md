# AI Job Intelligence Platform - Technical Design Document

**Version:** 1.0  
**Author:** Solution Architecture  
**Date:** June 11, 2026  
**Status:** Draft for Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Objective Analysis](#2-project-objective-analysis)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack Recommendations](#4-technology-stack-recommendations)
5. [Data Sources Strategy](#5-data-sources-strategy)
6. [AI/ML Strategy](#6-aiml-strategy)
7. [Database Design](#7-database-design)
8. [Project Roadmap](#8-project-roadmap)
9. [Legal, Technical & Scraping Limitations](#9-legal-technical--scraping-limitations)
10. [Folder Structure & Repository Organization](#10-folder-structure--repository-organization)
11. [Portfolio-Worthy Features](#11-portfolio-worthy-features)
12. [Detailed Implementation Plan](#12-detailed-implementation-plan)

---

## 1. Executive Summary

The **AI Job Intelligence Platform** is a personal portfolio project designed to automatically discover, analyze, score, and report on job opportunities that match your professional profile as a Business Operations Analyst with ERP expertise.

### Key Value Propositions

| For Recruiters | For You (Developer) |
|----------------|---------------------|
| Demonstrates real-world data pipeline skills | Showcases end-to-end system design |
| Proves proficiency in job market analysis | Demonstrates AI/ML integration skills |
| Highlights automation capabilities | Portfolio piece for BA/DA/ERP roles |

### Success Metrics

- **Coverage:** 5+ job boards integrated
- **Match Accuracy:** 85%+ relevance scoring
- **Automation:** Daily automated job discovery
- **Reporting:** Weekly personalized job reports

---

## 2. Project Objective Analysis

### 2.1 User Profile Summary

| Attribute | Value |
|-----------|-------|
| **Current Role** | Business Operations Analyst |
| **Core Skills** | ERP (SAP ECC, Odoo), SQL, Cost Control, Budgeting |
| **BI Tools** | Looker Studio, Google Sheets Automation |
| **Target Roles** | ERP Analyst, Business Analyst, Operations Analyst, Cost Control Analyst, Finance Analyst, Reporting Analyst, Data Analyst |
| **Target Locations** | Jakarta, Bekasi, Karawang, Remote |
| **Salary Range** | IDR 15M - 25M / month |

### 2.2 Functional Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORE SYSTEM FUNCTIONS                        │
├─────────────────────────────────────────────────────────────────┤
│  1. JOB DISCOVERY         → Search multiple job boards          │
│  2. DATA EXTRACTION       → Parse job postings automatically    │
│  3. PROFILE MATCHING      → Score jobs against your profile     │
│  4. DATA PERSISTENCE      → Store results in structured DB      │
│  5. REPORT GENERATION     → Create actionable insights          │
│  6. RECOMMENDATIONS       → Provide next-step actions           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Reliability** | 99% uptime for scheduled jobs |
| **Scalability** | Support 10+ job boards, 1000+ jobs/day |
| **Maintainability** | Clean code, comprehensive docs |
| **Portfolio Value** | Professional-grade, production-ready |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI JOB INTELLIGENCE PLATFORM                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐     │
│  │   JOB BOARD  │     │   JOB BOARD  │     │       JOB BOARD          │     │
│  │   (APIs /    │     │   (APIs /    │     │       (APIs /            │     │
│  │   Scrapers)  │     │   Scrapers)  │     │       Scrapers)          │     │
│  └──────┬───────┘     └──────┬───────┘     └──────────┬───────────────┘     │
│         │                    │                        │                      │
│         └────────────────────┼────────────────────────┘                      │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │    DATA LAYER        │                                   │
│                   │  ┌────────────────┐  │                                   │
│                   │  │ Extractors/    │  │                                   │
│                   │  │ Scrapers       │  │                                   │
│                   │  └───────┬────────┘  │                                   │
│                   │          ▼           │                                   │
│                   │  ┌────────────────┐  │                                   │
│                   │  │  ETL Pipeline  │  │                                   │
│                   │  │  (Transform)   │  │                                   │
│                   │  └───────┬────────┘  │                                   │
│                   └──────────┼───────────┘                                   │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │      DATABASE        │                                   │
│                   │   (PostgreSQL)       │                                   │
│                   │  ┌───────────────┐   │                                   │
│                   │  │ jobs          │   │                                   │
│                   │  │ profiles      │   │                                   │
│                   │  │ scores        │   │                                   │
│                   │  │ reports       │   │                                   │
│                   │  └───────────────┘   │                                   │
│                   └──────────┬───────────┘                                   │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │    AI/ML LAYER       │                                   │
│                   │  ┌────────────────┐  │                                   │
│                   │  │ Job Scorer     │  │                                   │
│                   │  │ Recommender    │  │                                   │
│                   │  │ NLP Processor  │  │                                   │
│                   │  └────────────────┘  │                                   │
│                   └──────────┬───────────┘                                   │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │    APPLICATION       │                                   │
│                   │       LAYER          │                                   │
│                   │  ┌────────────────┐  │                                   │
│                   │  │ Dashboard      │  │                                   │
│                   │  │ API Server     │  │                                   │
│                   │  │ Report Gen     │  │                                   │
│                   │  └────────────────┘  │                                   │
│                   └──────────────────────┘                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM COMPONENTS                               │
├────────────────────┬───────────────────────────────────────────────────┤
│    COMPONENT       │              DESCRIPTION                          │
├────────────────────┼───────────────────────────────────────────────────┤
│ Scraper Service    │ Fetches job listings from multiple sources        │
│ ETL Pipeline       │ Transforms raw data into structured format        │
│ Database           │ PostgreSQL for relational job data                 │
│ AI Scorer          │ Scores job matches using NLP and ML               │
│ Recommendation     │ Generates personalized job recommendations        │
│ Report Generator   │ Creates PDF/HTML reports                          │
│ Dashboard          │ Streamlit/Gradio web interface                    │
│ Scheduler          │ Cron-based automation for daily jobs              │
│ API Server         │ FastAPI for programmatic access                   │
└────────────────────┴───────────────────────────────────────────────────┘
```

---

## 4. Technology Stack Recommendations

### 4.1 Programming Language: Python

| Factor | Recommendation | Rationale |
|--------|----------------|-----------|
| **Primary Language** | Python 3.11+ | Rich ecosystem for web scraping, ML, and automation |
| **Scripting** | Python | Data processing, ETL pipelines |
| **Web Framework** | FastAPI | Modern, async, documentation auto-generation |
| **Dashboard** | Streamlit | Rapid UI development, perfect for data apps |

**Why Python?**

- **Scraping:** BeautifulSoup, Selenium, Playwright, Scrapy
- **ML/AI:** scikit-learn, transformers, sentence-transformers
- **Data:** pandas, numpy, sqlalchemy
- **Automation:** schedule, APScheduler, Prefect/Airflow
- **Dashboard:** Streamlit, Gradio, Plotly Dash

### 4.2 Database: PostgreSQL

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **PostgreSQL** | Robust, ACID compliant, JSON support, free | Requires setup | ✅ **Recommended** |
| SQLite | Simple, no setup | Limited concurrency | MVP only |
| MongoDB | Flexible schema | No joins | Not needed |
| Supabase | PostgreSQL + auto-API | Vendor lock-in | Consider for hosting |

**Schema Design:**

```sql
-- Core Tables
profiles              -- User professional profile
jobs                  -- Job postings (normalized)
job_sources           -- Job board sources
job_skills            -- Extracted skills from jobs
job_scores            -- Match scores per job
reports               -- Generated reports
recommendations       -- Actionable recommendations
```

### 4.3 AI Model Strategy

| Component | Approach | Model/Service |
|-----------|----------|---------------|
| **Skill Matching** | Embeddings + Cosine Similarity | sentence-transformers (all-MiniLM-L6-v2) |
| **Job Categorization** | Zero-shot Classification | transformers (facebook/bart-large-mnli) |
| **Salary Parsing** | Regex + NLP | Custom rules-based |
| **Summary Generation** | Text Summarization | transformers (sshleifer/distilbart-cnn-12-6) |
| **LLM Responses** | GPT-4 / Claude | OpenAI/Anthropic API |

**Why Local Models First?**

- No API costs during development
- Works offline
- Full control over data privacy
- Demonstrates ML expertise

### 4.4 Hosting Strategy

| Phase | Recommended Hosting | Cost | Effort |
|-------|---------------------|------|--------|
| **MVP** | Local/Railway/Render | Free | Low |
| **V2** | Railway + Supabase | ~$10/mo | Medium |
| **V3** | DigitalOcean App Platform | ~$20/mo | Medium |

**Deployment Options:**

| Service | Pros | Cons | Best For |
|---------|------|------|----------|
| **Railway** | Easy deployment, PostgreSQL included | Limited free tier | Quick MVP |
| **Render** | Free tier, Python support | Cold starts | Production |
| **DigitalOcean App Platform** | Scalable, predictable pricing | More complex | V3 production |
| **Hetzner Cloud** | Affordable, full control | Manual setup | Self-hosted |

### 4.5 Reporting Strategy

| Report Type | Format | Generation Method |
|-------------|--------|-------------------|
| **Daily Digest** | Email/HTML | Automated email via SendGrid |
| **Weekly Summary** | PDF | WeasyPrint / ReportLab |
| **Dashboard** | Web UI | Streamlit |
| **Export** | CSV/Excel | pandas |

---

## 5. Data Sources Strategy

### 5.1 Primary Job Boards

| Source | API Available | Scraping Difficulty | Data Quality |
|--------|---------------|---------------------|--------------|
| **LinkedIn** | Limited (Premium) | High | ⭐⭐⭐⭐⭐ |
| **JobStreet** | Partner API only | Medium | ⭐⭐⭐⭐ |
| **Glints** | No official API | Medium | ⭐⭐⭐⭐ |
| **Kalibrr** | No official API | Medium | ⭐⭐⭐⭐ |
| **Indeed** | Limited | Low | ⭐⭐⭐ |
| **Glassdoor** | Limited | High | ⭐⭐⭐ |
| **JobsDB (via JobStreet)** | Partner API only | Medium | ⭐⭐⭐⭐ |

### 5.2 Data Extraction Methods

```
┌─────────────────────────────────────────────────────────────────┐
│                   DATA EXTRACTION STRATEGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Priority 1: OFFICIAL APIs                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LinkedIn Jobs API (if premium)                         │    │
│  │  JobStreet Partner API (if available)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Priority 2: RSS FEEDS & SEARCH URLS                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Indeed RSS (limited)                                   │    │
│  │  Custom search URL parsing                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Priority 3: ETHICAL SCRAPING                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Respect robots.txt                                     │    │
│  │  Rate limiting (1 request/second)                       │    │
│  │  Cache responses (24-hour TTL)                          │    │
│  │  User-agent transparency                                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Job Data Schema

```python
class JobPosting:
    source: str              # "linkedin", "jobstreet", "glints"
    source_id: str           # Original job ID from source
    title: str               # Job title
    company: str             # Company name
    location: str            # City/Region
    is_remote: bool          # Remote work indicator
    salary_min: int          # Monthly salary (IDR)
    salary_max: int          # Monthly salary (IDR)
    currency: str            # "IDR"
    description: str         # Full job description
    requirements: List[str]  # Extracted requirements
    skills: List[str]        # Extracted skills
    posted_date: datetime    # When posted
    apply_url: str           # Direct application link
    scraped_at: datetime     # When we scraped it
```

### 5.4 Search Query Strategy

| Role Type | Search Terms |
|-----------|--------------|
| ERP Analyst | "ERP Analyst", "SAP Analyst", "Odoo Analyst", "ERP Consultant" |
| Business Analyst | "Business Analyst", "BA", "Functional Consultant" |
| Operations Analyst | "Operations Analyst", "Process Analyst", "Operations Excellence" |
| Finance/Cost Analyst | "Finance Analyst", "Cost Analyst", "Budget Analyst", "Cost Control" |
| Data/Reporting Analyst | "Data Analyst", "Reporting Analyst", "BI Analyst", "SQL Analyst" |

**Location Filters:**
- Jakarta (Greater Jakarta area)
- Bekasi
- Karawang
- "Remote" OR "Work from Home" OR "Hybrid"

**Salary Filter:** 15,000,000 - 25,000,000 IDR

---

## 6. AI/ML Strategy

### 6.1 Job Scoring Algorithm

```python
"""
Job Match Score Calculation
============================
Weighted scoring based on profile alignment
"""

def calculate_job_match_score(job: JobPosting, profile: Profile) -> float:
    """
    Calculate overall match score (0-100)
    
    Weights:
    - Skills Match: 40%
    - Role Title Match: 30%
    - Location Match: 15%
    - Salary Match: 10%
    - Experience Level: 5%
    """
    skills_score = calculate_skills_match(job.skills, profile.skills) * 0.40
    title_score = calculate_title_match(job.title, profile.target_roles) * 0.30
    location_score = calculate_location_match(job, profile) * 0.15
    salary_score = calculate_salary_match(job, profile) * 0.10
    experience_score = calculate_experience_match(job, profile) * 0.05
    
    return skills_score + title_score + location_score + salary_score + experience_score
```

### 6.2 NLP Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    NLP PIPELINE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Raw Job Text ──► Cleaning ──► Skill Extraction ──► Scoring     │
│       │              │              │                │           │
│       ▼              ▼              ▼                ▼           │
│  - HTML tags    - Lowercase    - NLP entity     - Cosine sim    │
│  - Special      - Remove       - Keyword match   - Weighted     │
│    characters     punctuation  - ML classification   scoring    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Skills Taxonomy

```python
SKILLS_TAXONOMY = {
    "technical": [
        "SAP ECC", "SAP S/4HANA", "Odoo", "SQL", "Python",
        "Excel", "Google Sheets", "Looker Studio", "Power BI",
        "Tableau", "ETL", "Data Modeling"
    ],
    "business": [
        "Business Analysis", "Process Improvement", "Cost Control",
        "Budgeting", "Financial Analysis", "Requirements Gathering",
        "Stakeholder Management", "Project Management"
    ],
    "soft": [
        "Communication", "Problem Solving", "Analytical Thinking",
        "Team Collaboration", "Presentation"
    ]
}
```

---

## 7. Database Design

### 7.1 Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   profiles   │       │     jobs     │       │  job_sources │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ name         │       │ source_id    │       │ name         │
│ skills       │       │ source (FK)  │       │ base_url     │
│ target_roles │       │ title        │       │ api_key      │
│ locations    │       │ company      │       │ is_active    │
│ salary_min   │       │ location     │       └──────────────┘
│ salary_max   │       │ is_remote    │
│ created_at   │       │ salary_min   │       ┌──────────────┐
└──────────────┘       │ salary_max   │       │ job_skills   │
        │              │ description  │       ├──────────────┤
        │              │ requirements │       │ id (PK)      │
        │              │ apply_url    │       │ job_id (FK)  │
        │              │ posted_date  │       │ skill_name   │
        │              │ scraped_at   │       │ confidence   │
        │              │ is_active    │       └──────────────┘
        │              └──────────────┘
        │                      │
        ▼                      ▼
┌──────────────┐       ┌──────────────┐
│ job_scores   │       │recommendations│
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ profile_id   │       │ profile_id   │
│ job_id (FK)  │       │ job_id (FK)  │
│ total_score  │       │ recommendation│
│ skills_score │       │ priority     │
│ title_score  │       │ created_at   │
│ location_score│      │ is_read      │
│ salary_score │       └──────────────┘
│ created_at   │
└──────────────┘
```

### 7.2 SQL Schema

```sql
-- profiles table
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    skills TEXT[], -- PostgreSQL array
    target_roles TEXT[],
    preferred_locations TEXT[],
    salary_min INTEGER,
    salary_max INTEGER,
    experience_years INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100) NOT NULL,
    source VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    is_remote BOOLEAN DEFAULT FALSE,
    salary_min INTEGER,
    salary_max INTEGER,
    description TEXT,
    requirements TEXT,
    apply_url TEXT,
    posted_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(source, source_id)
);

-- job_skills table
CREATE TABLE job_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    UNIQUE(job_id, skill_name)
);

-- job_scores table
CREATE TABLE job_scores (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    total_score FLOAT,
    skills_score FLOAT,
    title_score FLOAT,
    location_score FLOAT,
    salary_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_id, job_id)
);

-- recommendations table
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50),
    priority INTEGER DEFAULT 3,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_posted ON jobs(posted_date DESC);
CREATE INDEX idx_job_scores_profile ON job_scores(profile_id);
CREATE INDEX idx_job_scores_job ON job_scores(job_id);
CREATE INDEX idx_recommendations_profile ON recommendations(profile_id);
```

---

## 8. Project Roadmap

### 8.1 Version Timeline

```
Timeline (12 weeks)
═══════════════════════════════════════════════════════════════════

Week 1-2     │ Week 3-4     │ Week 5-6     │ Week 7-9    │ Week 10-12
─────────────┼──────────────┼──────────────┼─────────────┼─────────────
MVP          │ MVP          │ Version 2    │ Version 2   │ Version 3
Development  │ Polish       │ Development  │ Polish      │ Development
             │ & Launch     │              │ & Launch    │
```

### 8.2 MVP (Weeks 1-4)

**Goal:** Core functionality - job scraping, basic scoring, dashboard

#### Features

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| 1 | Profile Setup | User profile with skills, roles, locations | P0 |
| 2 | Manual Job Input | Add jobs manually for testing | P0 |
| 3 | Basic Job Scraper | Scrape from 1-2 job boards | P0 |
| 4 | Skills Matching | Match job skills to profile | P0 |
| 5 | Simple Dashboard | Streamlit dashboard showing matches | P0 |
| 6 | SQLite Database | Local data persistence | P1 |
| 7 | Job Alerts | Email notification for new matches | P2 |

#### Deliverables

- [ ] Working scraper for Indeed OR Glints
- [ ] Basic skills matching algorithm
- [ ] Streamlit dashboard with top 20 job matches
- [ ] SQLite database with job data
- [ ] GitHub repository with documentation

#### Portfolio Evidence

```
✅ Demonstrates: Web scraping, data processing, basic ML
✅ Tech Stack: Python, SQLite, Streamlit
✅ Shows: End-to-end data pipeline
```

### 8.3 Version 2 (Weeks 5-9)

**Goal:** Multiple sources, advanced scoring, reporting

#### Features

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| 1 | Multi-Source Scraping | JobStreet, Glints, LinkedIn | P0 |
| 2 | PostgreSQL Migration | Production database | P0 |
| 3 | Advanced Scoring | Weighted scoring with NLP | P0 |
| 4 | Automated Scheduling | Daily job discovery | P0 |
| 5 | PDF Reports | Weekly job summary reports | P1 |
| 6 | FastAPI Backend | REST API for data access | P1 |
| 7 | Role Classification | Auto-categorize job types | P1 |
| 8 | Salary Analysis | Salary range trends | P2 |

#### Deliverables

- [ ] Scrapers for 4+ job boards
- [ ] PostgreSQL database on cloud
- [ ] ML-based job scoring
- [ ] FastAPI backend with documentation
- [ ] Automated daily scraping job
- [ ] Weekly PDF report generation
- [ ] Deployed web application

#### Portfolio Evidence

```
✅ Demonstrates: Multi-source data integration, ML pipeline
✅ Tech Stack: PostgreSQL, FastAPI, ML (scikit-learn/transformers)
✅ Shows: Production-ready deployment, automation
```

### 8.4 Version 3 (Weeks 10-12)

**Goal:** AI-powered insights, full automation, advanced analytics

#### Features

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| 1 | LLM Integration | GPT-4/Claude for job analysis | P0 |
| 2 | Cover Letter Gen | AI-generated cover letter drafts | P1 |
| 3 | Interview Prep | AI-generated interview questions | P1 |
| 4 | Market Analysis | Salary trends, demand analysis | P1 |
| 5 | Skill Gap Analysis | What skills to develop | P1 |
| 6 | Application Tracker | Track applied jobs | P1 |
| 7 | Dashboard Improvements | Interactive visualizations | P2 |
| 8 | Mobile Notifications | Push notifications | P2 |

#### Deliverables

- [ ] LLM-powered job analysis
- [ ] Cover letter generation
- [ ] Market analytics dashboard
- [ ] Application tracking system
- [ ] Deployed on cloud platform
- [ ] Production monitoring

#### Portfolio Evidence

```
✅ Demonstrates: LLM integration, advanced analytics
✅ Tech Stack: OpenAI API, advanced visualizations
✅ Shows: Full-stack development, production deployment
```

---

## 9. Legal, Technical & Scraping Limitations

### 9.1 Legal Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│                       LEGAL COMPLIANCE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ⚠️  CRITICAL: Always respect Terms of Service                  │
│                                                                  │
│  LinkedIn:                                                        │
│  - Prohibits scraping without consent                           │
│  - Has taken legal action against scrapers                      │
│  - Consider LinkedIn Premium API or manual input                │
│                                                                  │
│  JobStreet/Kalibrr/Glints:                                       │
│  - Terms prohibit automated scraping                             │
│  - Data is copyrighted material                                 │
│  - Use official APIs where available                            │
│                                                                  │
│  RECOMMENDATION:                                                 │
│  - Use official APIs when available                             │
│  - Implement polite scraping with delays                        │
│  - Consider this as a learning project, not production tool     │
│  - Don't commercialize without proper licensing                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Technical Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Rate Limiting** | May block scraping | Implement delays, use APIs |
| **Dynamic Content** | JavaScript-heavy sites | Use Selenium/Playwright |
| **CAPTCHA** | Blocks automated access | Use anti-CAPTCHA services |
| **Session Expiration** | Login required | OAuth flows where possible |
| **Data Format Changes** | Site redesigns break scrapers | Regular maintenance |
| **Anti-bot Detection** | IP blocking | Proxy rotation, headers |

### 9.3 Scraping Best Practices

```python
# Example: Ethical scraping configuration
SCRAPING_CONFIG = {
    "rate_limit": 1,           # 1 request per second
    "respect_robots_txt": True,
    "user_agent": "Job Search App - Educational Purpose Only",
    "cache_ttl": 3600,         # Cache for 1 hour
    "max_retries": 3,
    "timeout": 30,
    "random_delays": True,     # 1-3 seconds random delay
}
```

---

## 10. Folder Structure & Repository Organization

### 10.1 Project Folder Structure

```
ai-job-intelligence-platform/
│
├── README.md                     # Project overview
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # This document
│   ├── API_DOCUMENTATION.md     # API reference
│   ├── SETUP_GUIDE.md           # Installation guide
│   └── CONTRIBUTING.md          # Contribution guidelines
│
├── src/                          # Source code
│   ├── __init__.py
│   │
│   ├── config/                   # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py          # App settings
│   │   ├── database.py          # DB config
│   │   └── scraping.py          # Scraper config
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── profile.py
│   │   ├── job.py
│   │   └── score.py
│   │
│   ├── scrapers/                 # Web scrapers
│   │   ├── __init__.py
│   │   ├── base.py              # Base scraper class
│   │   ├── indeed_scraper.py
│   │   ├── glints_scraper.py
│   │   ├── jobstreet_scraper.py
│   │   └── linkedin_scraper.py
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── job_service.py       # Job operations
│   │   ├── scoring_service.py   # ML scoring
│   │   ├── nlp_service.py       # NLP processing
│   │   └── report_service.py    # Report generation
│   │
│   ├── api/                      # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/
│   │   │   ├── jobs.py
│   │   │   ├── profiles.py
│   │   │   └── reports.py
│   │   └── schemas/             # Pydantic models
│   │
│   ├── ml/                       # Machine learning
│   │   ├── __init__.py
│   │   ├── skill_matcher.py     # Skills matching
│   │   ├── job_classifier.py    # Job categorization
│   │   └── embeddings.py        # Text embeddings
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── validators.py
│       └── helpers.py
│
├── dashboard/                    # Streamlit dashboard
│   ├── app.py                    # Main dashboard
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_💼_Jobs.py
│   │   ├── 3_📈_Analytics.py
│   │   └── 4_⚙️_Settings.py
│   └── components/
│       ├── job_card.py
│       └── score_chart.py
│
├── scripts/                      # Automation scripts
│   ├── daily_scrape.py          # Daily job scraping
│   ├── generate_report.py       # Weekly report
│   └── seed_data.py             # Sample data
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_scrapers/
│   ├── test_services/
│   └── test_api/
│
├── migrations/                   # Database migrations
│   └── 001_initial_schema.sql
│
├── notebooks/                    # Jupyter notebooks
│   ├── eda_analysis.ipynb
│   └── model_training.ipynb
│
└── .env.example                 # Environment template
```

### 10.2 GitHub Repository Structure

```
github.com/yourusername/ai-job-intelligence-platform
│
├── 📄 README.md                 # Project showcase
├── 📄 LICENSE                   # MIT License
├── 📄 CONTRIBUTING.md           # Contribution guide
│
├── 🐳 .github/
│   └── workflows/
│       ├── ci.yml               # CI pipeline
│       └── deploy.yml           # Deployment pipeline
│
├── 📦 Package (pip installable)
│   └── src/                     # As shown above
│
└── 📱 Dashboard (separate entry point)
    └── dashboard/               # Streamlit app
```

### 10.3 Git Strategy

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Production code | Required PR, review |
| `develop` | Integration branch | Required PR |
| `feature/*` | Feature development | Open |
| `bugfix/*` | Bug fixes | Open |
| `hotfix/*` | Production fixes | Direct merge |

---

## 11. Portfolio-Worthy Features

### 11.1 For Business Analyst Roles

| Feature | Technical Implementation | Why It Impresses |
|---------|-------------------------|------------------|
| **Requirements Mapping** | Extract and map job requirements to profile skills | Shows BA understanding |
| **Gap Analysis Dashboard** | Visual skill gap between current profile and job requirements | Demonstrates analytical thinking |
| **Stakeholder Communication Report** | Generate executive summary reports | Proves communication skills |
| **Process Flow Visualization** | Show job discovery → scoring → recommendation workflow | Visual documentation skills |

### 11.2 For ERP Analyst Roles

| Feature | Technical Implementation | Why It Impresses |
|---------|-------------------------|------------------|
| **ERP-Specific Skill Matching** | Match SAP/Odoo experience to job requirements | Domain expertise |
| **Configuration Mapping** | Map job needs to ERP modules (FI, CO, MM, SD) | Deep ERP knowledge |
| **Integration Analysis** | Show how different ERP skills complement each other | System thinking |
| **Custom ERP Skill Taxonomy** | Develop hierarchical skill categories for ERP systems | Structured thinking |

### 11.3 For Operations Analyst Roles

| Feature | Technical Implementation | Why It Impresses |
|---------|-------------------------|------------------|
| **Process Optimization Dashboard** | Show time saved by automated job discovery | Efficiency mindset |
| **KPI Tracking** | Track application success rate, response time | Metrics-driven |
| **Workflow Automation** | End-to-end automated pipeline | Process improvement |
| **Root Cause Analysis** | Analyze why certain jobs don't match | Analytical skills |

### 11.4 For Data Analyst Roles

| Feature | Technical Implementation | Why It Impresses |
|---------|-------------------------|------------------|
| **SQL Analytics Pipeline** | Complex queries for job market analysis | SQL proficiency |
| **Data Quality Monitoring** | Track scraping success rate, data completeness | Data quality mindset |
| **Statistical Scoring Model** | ML-based job matching with explainability | ML/Stats knowledge |
| **Interactive Visualizations** | Plotly dashboards with filters | Data visualization |

### 11.5 Showcase-Worthy Code Examples

```python
# Example 1: Skills Matching with Embeddings (Data Analyst)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SkillMatcher:
    """Matches job skills to profile using semantic embeddings"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def calculate_similarity(self, profile_skills: List[str], job_skills: List[str]) -> float:
        """Calculate semantic similarity between skill sets"""
        profile_embeddings = self.model.encode(profile_skills)
        job_embeddings = self.model.encode(job_skills)
        
        similarity_matrix = cosine_similarity(profile_embeddings, job_embeddings)
        max_similarities = np.max(similarity_matrix, axis=1)
        
        return float(np.mean(max_similarities))

# Example 2: ETL Pipeline (Data Engineer)
import pandas as pd
from sqlalchemy import create_engine

class JobETL:
    """Extract, Transform, Load pipeline for job data"""
    
    def extract(self, scraper: BaseScraper) -> List[dict]:
        """Extract raw job data from source"""
        return scraper.scrape()
    
    def transform(self, raw_jobs: List[dict]) -> pd.DataFrame:
        """Transform and clean job data"""
        df = pd.DataFrame(raw_jobs)
        df['salary_min'] = df['salary'].apply(self._extract_min_salary)
        df['salary_max'] = df['salary'].apply(self._extract_max_salary)
        df['skills'] = df['description'].apply(self._extract_skills)
        df['posted_days_ago'] = (pd.Timestamp.now() - df['posted_date']).dt.days
        return df
    
    def load(self, df: pd.DataFrame, table_name: str):
        """Load to database with upsert logic"""
        engine = create_engine(os.getenv('DATABASE_URL'))
        df.to_sql(table_name, engine, if_exists='append', index=False)

# Example 3: Job Scoring (Business Analyst)
class JobScorer:
    """Scores jobs based on profile alignment"""
    
    WEIGHTS = {
        'skills_match': 0.40,
        'role_match': 0.30,
        'location_match': 0.15,
        'salary_match': 0.10,
        'experience_match': 0.05
    }
    
    def score(self, job: Job, profile: Profile) -> JobScore:
        """Calculate weighted match score"""
        return JobScore(
            total=sum(
                getattr(self, f'_score_{criterion}')(job, profile) * weight
                for criterion, weight in self.WEIGHTS.items()
            ),
            breakdown={
                criterion: getattr(self, f'_score_{criterion}')(job, profile)
                for criterion in self.WEIGHTS
            }
        )
```

---

## 12. Detailed Implementation Plan

### 12.1 Task Breakdown by Week

#### Week 1: Project Setup & Profile

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 1.1 | Create GitHub repo and clone locally | 30 min | None |
| 1.2 | Set up Python virtual environment | 15 min | 1.1 |
| 1.3 | Create folder structure | 30 min | 1.1 |
| 1.4 | Install dependencies (streamlit, requests, bs4) | 15 min | 1.2 |
| 1.5 | Create Profile model with Pydantic | 1 hr | None |
| 1.6 | Create SQLite database schema | 1 hr | 1.5 |
| 1.7 | Create profile CRUD operations | 2 hr | 1.6 |
| 1.8 | Write unit tests for profile model | 1 hr | 1.5, 1.6 |

**Deliverable:** Profile management system with database

#### Week 2: Basic Scraper & Dashboard

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 2.1 | Create base scraper class | 2 hr | 1.4 |
| 2.2 | Implement Indeed scraper | 3 hr | 2.1 |
| 2.3 | Create Job model with Pydantic | 1 hr | 1.5 |
| 2.4 | Create job CRUD operations | 2 hr | 2.2, 2.3 |
| 2.5 | Create basic Streamlit dashboard | 2 hr | 2.4 |
| 2.6 | Display job list in dashboard | 1 hr | 2.5 |
| 2.7 | Add job filtering (location, salary) | 1 hr | 2.6 |
| 2.8 | Write tests for scraper | 2 hr | 2.2 |

**Deliverable:** Working scraper + dashboard showing scraped jobs

#### Week 3: Skills Matching

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 3.1 | Create skills taxonomy dictionary | 1 hr | None |
| 3.2 | Implement skills extraction from job text | 3 hr | 2.3 |
| 3.3 | Create skills matching algorithm | 2 hr | 3.1, 3.2 |
| 3.4 | Add scoring to database schema | 1 hr | 1.6 |
| 3.5 | Calculate and store scores | 2 hr | 3.3, 3.4 |
| 3.6 | Display scores in dashboard | 1 hr | 2.5, 3.5 |
| 3.7 | Add job sorting by score | 1 hr | 3.6 |
| 3.8 | Write tests for matching | 2 hr | 3.3 |

**Deliverable:** Jobs scored and ranked by match

#### Week 4: MVP Polish & Documentation

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 4.1 | Add error handling to scrapers | 2 hr | 2.2 |
| 4.2 | Add logging throughout app | 1 hr | None |
| 4.3 | Create .env.example file | 15 min | None |
| 4.4 | Update README with setup instructions | 1 hr | All |
| 4.5 | Add sample data script | 1 hr | 1.6 |
| 4.6 | Test on fresh environment | 1 hr | 4.1-4.5 |
| 4.7 | Push to GitHub, create PR | 30 min | 4.6 |
| 4.8 | Create demo video/screenshots | 2 hr | 2.5 |

**Deliverable:** Production-ready MVP

#### Week 5-6: Multi-Source & PostgreSQL

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 5.1 | Set up PostgreSQL (local or cloud) | 1 hr | None |
| 5.2 | Create PostgreSQL schema | 1 hr | 5.1 |
| 5.3 | Update config for PostgreSQL | 1 hr | 5.2 |
| 5.4 | Implement Glints scraper | 3 hr | 2.1 |
| 5.5 | Implement JobStreet scraper | 3 hr | 2.1 |
| 5.6 | Create job deduplication logic | 2 hr | 5.4, 5.5 |
| 5.7 | Create ETL pipeline | 3 hr | 5.3, 5.6 |
| 5.8 | Write tests for new scrapers | 2 hr | 5.4, 5.5 |

#### Week 7-8: Advanced Scoring & API

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 7.1 | Set up FastAPI project | 1 hr | 5.3 |
| 7.2 | Create API endpoints for jobs | 3 hr | 7.1 |
| 7.3 | Create API endpoints for profiles | 2 hr | 7.1 |
| 7.4 | Implement API authentication | 2 hr | 7.2 |
| 7.5 | Add weighted scoring algorithm | 3 hr | 3.3 |
| 7.6 | Implement location matching | 2 hr | 7.5 |
| 7.7 | Implement salary matching | 2 hr | 7.5 |
| 7.8 | Update dashboard to use API | 2 hr | 7.2, 2.5 |

#### Week 9-10: Automation & Reporting

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 9.1 | Set up APScheduler | 1 hr | 5.3 |
| 9.2 | Create daily scraping job | 2 hr | 9.1, 5.7 |
| 9.3 | Create email notification service | 3 hr | 9.2 |
| 9.4 | Set up WeasyPrint | 1 hr | None |
| 9.5 | Create PDF report template | 3 hr | 9.4 |
| 9.6 | Generate weekly report script | 3 hr | 9.5 |
| 9.7 | Deploy to Railway/Render | 2 hr | 9.1-9.6 |
| 9.8 | Set up GitHub Actions CI | 2 hr | 9.7 |

#### Week 11-12: AI Integration & Polish

| Task | Description | Estimated Time | Dependencies |
|------|-------------|----------------|--------------|
| 11.1 | Set up OpenAI API | 1 hr | None |
| 11.2 | Create LLM job analyzer | 3 hr | 11.1 |
| 11.3 | Implement cover letter generator | 4 hr | 11.2 |
| 11.4 | Create interview prep generator | 4 hr | 11.2 |
| 11.5 | Build analytics dashboard | 3 hr | 7.8 |
| 11.6 | Add market trends visualization | 3 hr | 11.5 |
| 11.7 | Performance optimization | 2 hr | All |
| 11.8 | Final testing and bug fixes | 4 hr | 11.1-11.7 |
| 11.9 | Documentation finalization | 3 hr | All |
| 11.10 | Portfolio presentation | 2 hr | 11.9 |

### 12.2 Daily Task Template

```markdown
## Daily Task Template

**Date:** [YYYY-MM-DD]
**Focus:** [Feature/Component]

### Tasks
- [ ] Task 1: [Description] (Est: X hr)
- [ ] Task 2: [Description] (Est: X hr)

### Progress
- Completed: [What was done]
- Blockers: [Any issues]
- Tomorrow: [Next steps]

### Notes
[Any observations or learnings]
```

### 12.3 Beginner Developer Checklist

```markdown
## Before You Start
- [ ] Python installed (3.11+)
- [ ] Git installed
- [ ] GitHub account created
- [ ] IDE configured (VS Code recommended)
- [ ] PostgreSQL installed (or use cloud)

## Weekly Checkpoints
- [ ] All code committed to Git
- [ ] Tests passing
- [ ] No TODO comments left
- [ ] Documentation updated
- [ ] Dashboard working

## Pre-Merge Checklist
- [ ] Code reviewed by self
- [ ] No hardcoded secrets
- [ ] Environment variables documented
- [ ] README updated
- [ ] Demo tested
```

---

## 13. Risk Assessment & Mitigation

### 13.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Job board blocks scraping | High | Medium | Use APIs, rotate sources |
| Site redesign breaks scrapers | High | High | Modular design, regular maintenance |
| LLM API costs spiral | Medium | High | Set budget limits, use local models |
| Database performance issues | Low | Medium | Proper indexing, query optimization |

### 13.2 Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | Medium | High | Strict MVP definition |
| Skill gap on ML components | Medium | Medium | Start with simple algorithms |
| Time constraints | High | High | Prioritize ruthlessly |

---

## 14. Success Criteria

### 14.1 MVP Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Jobs scraped daily | 50+ | Count in database |
| Match accuracy | 80%+ | Manual verification |
| Dashboard uptime | 95%+ | Uptime monitor |
| Test coverage | 70%+ | pytest --cov |

### 14.2 Version 2 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Job boards integrated | 4+ | Count sources |
| Scoring algorithm accuracy | 85%+ | User feedback |
| Report generation | Weekly | Automated schedule |
| API response time | <500ms | Performance testing |

### 14.3 Version 3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| LLM integration | 3+ features | Feature count |
| Application tracking | Functional | User testing |
| Market analytics | Complete | Dashboard review |
| Production deployment | Stable | 30-day uptime |

---

## 15. Appendix

### A. Recommended Learning Resources

| Topic | Resource |
|-------|----------|
| Web Scraping | Real Python - Web Scraping with Python |
| FastAPI | FastAPI Documentation |
| Streamlit | Streamlit Documentation |
| ML | scikit-learn User Guide |
| NLP | Hugging Face Transformers Course |
| PostgreSQL | PostgreSQL Tutorial |

### B. Alternative Approaches Considered

| Approach | Why Not Chosen |
|----------|----------------|
| No-code platform (Zapier) | Limited customization, not portfolio-worthy |
| Node.js backend | Python better for ML/NLP |
| MongoDB | Relational data better fits schema |
| AWS Lambda | More complex, higher cost for this use case |

### C. Future Enhancements

- LinkedIn Easy Apply automation
- Job application tracking with calendar
- Salary negotiation insights
- Interview scheduling integration
- Multi-language support (Bahasa Indonesia)

---

**Document Version:** 1.0  
**Last Updated:** June 11, 2026  
**Next Review:** After MVP completion