# AI Job Intelligence Platform

## Intelligent Job Discovery, Matching & Career Intelligence System

A comprehensive platform that automatically discovers job opportunities matching your professional profile, scores them using AI, and provides actionable recommendations.

---

## 🎯 Project Overview

This platform helps professionals (Business Analysts, ERP Analysts, Operations Analysts, Data Analysts) find and evaluate job opportunities by:

- **Auto-discovering** jobs from multiple job boards (LinkedIn, JobStreet, Glints, Kalibrr, Indeed)
- **Scoring** jobs against your professional profile using AI/ML
- **Analyzing** salary ranges, skill requirements, and job fit
- **Generating** personalized reports and recommendations
- **Tracking** application status and interview preparation

---

## 📋 Target Profile

| Attribute | Value |
|-----------|-------|
| **Current Role** | Business Operations Analyst |
| **Core Skills** | ERP (SAP ECC, Odoo), SQL, Cost Control, Budgeting |
| **BI Tools** | Looker Studio, Google Sheets Automation |
| **Target Roles** | ERP Analyst, Business Analyst, Operations Analyst, Cost Control Analyst, Finance Analyst, Reporting Analyst, Data Analyst |
| **Target Locations** | Jakarta, Bekasi, Karawang, Remote |
| **Salary Range** | IDR 15M - 25M / month |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI JOB INTELLIGENCE PLATFORM                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐     │
│  │   LinkedIn   │     │  JobStreet   │     │       Glints             │     │
│  │   (API/      │     │   (Scraper)  │     │       (Scraper)          │     │
│  │   Manual)    │     │              │     │                          │     │
│  └──────┬───────┘     └──────┬───────┘     └──────────┬───────────────┘     │
│         │                    │                        │                      │
│         └────────────────────┼────────────────────────┘                      │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │    ETL Pipeline      │                                   │
│                   │  (Extract/Transform) │                                   │
│                   └──────────┬───────────┘                                   │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │   PostgreSQL         │                                   │
│                   │   Database           │                                   │
│                   └──────────┬───────────┘                                   │
│                              ▼                                               │
│                   ┌──────────────────────┐                                   │
│                   │   AI/ML Layer        │                                   │
│                   │  - Skills Matching   │                                   │
│                   │  - Job Scoring       │                                   │
│                   │  - NLP Processing    │                                   │
│                   └──────────┬───────────┘                                   │
│                              ▼                                               │
│         ┌────────────────────┼────────────────────┐                          │
│         ▼                    ▼                    ▼                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   FastAPI    │    │  Streamlit   │    │    PDF       │                   │
│  │   Backend    │    │  Dashboard   │    │   Reports    │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Roadmap

### MVP (Weeks 1-4)
- Profile setup with skills, roles, locations
- Basic job scraper (Indeed/Glints)
- Skills matching algorithm
- Streamlit dashboard with job matches

### Version 2 (Weeks 5-9)
- Multi-source scraping (4+ job boards)
- PostgreSQL database
- FastAPI backend
- Automated daily scheduling
- Weekly PDF reports

### Version 3 (Weeks 10-12)
- LLM integration (GPT-4/Claude)
- Cover letter generation
- Interview preparation AI
- Market analytics dashboard
- Production deployment

---

## 📁 Project Structure

```
ai-job-intelligence-platform/
├── docs/                          # Documentation
│   └── TECHNICAL_DESIGN_*.md      # Full technical design document
├── src/                           # Source code
│   ├── config/                    # Configuration
│   ├── models/                    # Data models
│   ├── scrapers/                  # Job board scrapers
│   ├── services/                  # Business logic
│   ├── api/                       # FastAPI endpoints
│   ├── ml/                        # Machine learning
│   └── utils/                     # Utilities
├── dashboard/                     # Streamlit dashboard
├── scripts/                       # Automation scripts
├── tests/                         # Unit tests
└── README.md                      # This file
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.11+ | Primary development |
| **Database** | PostgreSQL | Data persistence |
| **API** | FastAPI | REST API backend |
| **Dashboard** | Streamlit | Web UI |
| **ML** | scikit-learn, sentence-transformers | Job matching |
| **LLM** | OpenAI GPT-4 | AI features |
| **Scraping** | BeautifulSoup, Playwright | Job discovery |
| **Scheduling** | APScheduler | Automation |
| **Reports** | WeasyPrint | PDF generation |

---

## 📚 Documentation

- **[Technical Design Document](docs/TECHNICAL_DESIGN_AI_JOB_INTELLIGENCE_PLATFORM.md)** - Complete architecture, database schema, implementation plan

---

## ⚠️ Legal Notice

This project is for **educational and personal use** only. When scraping job boards:

- Respect Terms of Service
- Implement rate limiting (1 req/sec)
- Use official APIs when available
- Don't commercialize without proper licensing

---

## 📄 License

MIT License

---

*Built with OpenHands Agent*