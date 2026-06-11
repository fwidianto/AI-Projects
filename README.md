# AI Job Intelligence Platform

## Intelligent Job Discovery, Matching & Career Intelligence System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A comprehensive platform that automatically discovers job opportunities matching your professional profile, scores them using AI, and provides actionable recommendations.

---

## 🎯 Project Overview

This platform helps professionals find and evaluate job opportunities by:

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

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or SQLite for development)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/fwidianto/AI-Projects.git
cd AI-Projects

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# DATABASE_URL=postgresql://user:password@localhost:5432/job_intelligence
# OPENAI_API_KEY=your-api-key

# Initialize database
python -m scripts.init_db

# Run dashboard
streamlit run dashboard/app.py
```

### Or with Docker

```bash
# Build and run
docker-compose up -d

# Access dashboard at http://localhost:8501
```

---

## 📁 Project Structure

```
ai-job-intelligence-platform/
├── src/                           # Source code
│   ├── config/                    # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py            # App settings
│   │   ├── database.py            # DB config
│   │   └── scraping.py            # Scraper config
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── profile.py             # User profile model
│   │   ├── job.py                 # Job posting model
│   │   └── score.py               # Job score model
│   ├── scrapers/                  # Job board scrapers
│   │   ├── __init__.py
│   │   ├── base.py                # Base scraper class
│   │   ├── indeed_scraper.py
│   │   ├── glints_scraper.py
│   │   ├── jobstreet_scraper.py
│   │   └── linkedin_scraper.py
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── job_service.py         # Job operations
│   │   ├── scoring_service.py     # ML scoring
│   │   ├── nlp_service.py         # NLP processing
│   │   └── report_service.py      # Report generation
│   ├── api/                       # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py
│   │   │   ├── profiles.py
│   │   │   └── reports.py
│   │   └── schemas/               # Pydantic models
│   │       ├── __init__.py
│   │       ├── job.py
│   │       └── profile.py
│   ├── ml/                        # Machine learning
│   │   ├── __init__.py
│   │   ├── skill_matcher.py       # Skills matching
│   │   ├── job_classifier.py      # Job categorization
│   │   └── embeddings.py          # Text embeddings
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── validators.py
│       └── helpers.py
├── dashboard/                     # Streamlit dashboard
│   ├── app.py                     # Main dashboard
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_💼_Jobs.py
│   │   ├── 3_📈_Analytics.py
│   │   └── 4_⚙️_Settings.py
│   └── components/
│       ├── job_card.py
│       └── score_chart.py
├── scripts/                       # Automation scripts
│   ├── init_db.py                 # Database initialization
│   ├── daily_scrape.py            # Daily job scraping
│   ├── generate_report.py         # Weekly report
│   └── seed_data.py               # Sample data
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_scrapers/
│   ├── test_services/
│   └── test_api/
├── migrations/                    # Database migrations
│   └── 001_initial_schema.sql
├── notebooks/                    # Jupyter notebooks
│   ├── eda_analysis.ipynb
│   └── model_training.ipynb
├── data/                         # Sample data files
├── docs/                         # Documentation
│   ├── TECHNICAL_DESIGN_*.md
│   └── API_DOCUMENTATION.md
├── .env.example                  # Environment template
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── pyproject.toml
└── docker-compose.yml
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

## 🚀 Roadmap

### MVP (Weeks 1-4)
- [x] Project structure and documentation
- [ ] Profile setup with skills, roles, locations
- [ ] Basic job scraper (Indeed/Glints)
- [ ] Skills matching algorithm
- [ ] Streamlit dashboard with job matches

### Version 2 (Weeks 5-9)
- [ ] Multi-source scraping (4+ job boards)
- [ ] PostgreSQL database
- [ ] FastAPI backend
- [ ] Automated daily scheduling
- [ ] Weekly PDF reports

### Version 3 (Weeks 10-12)
- [ ] LLM integration (GPT-4/Claude)
- [ ] Cover letter generation
- [ ] Interview preparation AI
- [ ] Market analytics dashboard
- [ ] Production deployment

---

## 📚 Documentation

- **[Technical Design Document](docs/TECHNICAL_DESIGN_AI_JOB_INTELLIGENCE_PLATFORM.md)** - Complete architecture, database schema, implementation plan
- **[API Documentation](docs/API_DOCUMENTATION.md)** - REST API reference

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_services/

# Run with verbose output
pytest -v
```

---

## 📦 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ⚠️ Legal Notice

This project is for **educational and personal use** only. When scraping job boards:

- Respect Terms of Service
- Implement rate limiting (1 req/sec)
- Use official APIs when available
- Don't commercialize without proper licensing

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👤 Author

Built with OpenHands Agent on behalf of [@fwidianto](https://github.com/fwidianto)

---

*Last Updated: June 2026*