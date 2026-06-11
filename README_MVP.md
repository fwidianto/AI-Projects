# AI Job Intelligence Platform - MVP

## Quick Start

```bash
# 1. Install dependencies
pip install -r mvp_requirements.txt

# 2. Setup sample data (creates config and sample jobs)
python main.py --setup

# 3. Run full pipeline (scrape → score → report)
python main.py --all

# Or run individual commands:
python main.py --scrape --use-sample   # Use sample data (no web scraping)
python main.py --score               # Score jobs
python main.py --report               # Generate reports
```

---

## Project Structure

```
ai-job-intelligence-platform/
├── mvp/                      # MVP implementation
│   ├── config_loader.py     # Load profile from JSON
│   ├── database.py          # SQLite database manager
│   ├── scraper.py           # Job scraper + sample jobs
│   ├── scoring.py           # Rule-based job scoring
│   ├── export.py            # CSV export functionality
│   └── report.py            # Report generators
├── config/
│   └── profile.json         # Your profile configuration
├── data/                    # Output directory
│   ├── jobs.db              # SQLite database
│   ├── job_report.txt       # Text report
│   ├── job_report.html      # HTML report
│   └── jobs_export.csv     # CSV export
├── main.py                  # CLI entry point
└── mvp_requirements.txt     # Dependencies
```

---

## Features

### 1. Profile Configuration
Edit `config/profile.json` to set:
- **Target roles:** Jobs you're interested in
- **Skills:** Your professional skills with proficiency levels
- **Locations:** Preferred work locations
- **Salary expectations:** Min/max salary in IDR

### 2. Job Scraping
- Uses Indeed public search (rate limited)
- Or use sample jobs for testing
- Stores results in SQLite database

### 3. Rule-Based Scoring
Weights for scoring:
| Component | Weight | Description |
|-----------|--------|-------------|
| Skills Match | 40% | Match job requirements to profile skills |
| Title Match | 30% | Match job title to target roles |
| Location Match | 15% | Check location preferences |
| Salary Match | 10% | Check salary range overlap |
| Experience Match | 5% | Check years requirement |

### 4. Reports
Generates:
- **Text report:** `data/job_report.txt`
- **HTML report:** `data/job_report.html` (styled)
- **Markdown report:** `data/job_report.md`
- **CSV export:** `data/jobs_export.csv`

---

## CLI Commands

```bash
# Setup sample data
python main.py --setup

# Scrape jobs (or use --use-sample for demo)
python main.py --scrape
python main.py --scrape --use-sample

# Score jobs against profile
python main.py --score

# Generate reports
python main.py --report

# Run everything
python main.py --all

# View stats
python main.py --stats

# Show profile
python main.py --profile

# Custom options
python main.py --scrape --location "Jakarta" --max-results 100
```

---

## Assumptions & Limitations

### Assumptions
1. **SQLite is sufficient** for MVP (single user, <100K jobs)
2. **Keyword matching** is sufficient for skills matching (no ML embeddings)
3. **Indonesian job market** (salary in IDR, locations in Jakarta area)
4. **Indeed public pages** are accessible without login

### Limitations
1. **Scraping** - May break if Indeed changes HTML structure
2. **Rate limiting** - Limited to ~30 requests/minute
3. **No authentication** - Can't access LinkedIn or premium job boards
4. **Rule-based scoring** - May not capture semantic similarity

---

## Customization

### Add more skills to profile.json:
```json
{
  "name": "Skill Name",
  "proficiency": 5,
  "is_key_skill": true
}
```

### Adjust scoring weights:
```json
{
  "scoring_weights": {
    "skills_match": 0.40,
    "title_match": 0.30,
    "location_match": 0.15,
    "salary_match": 0.10,
    "experience_match": 0.05
  }
}
```

### Change search sources:
```json
{
  "search_preferences": {
    "sources": ["indeed", "linkedin"],
    "default_location": "Jakarta"
  }
}
```

---

## Next Steps (V2)

- [ ] Add more job sources (Glints, JobStreet)
- [ ] Implement ML-based skill matching (sentence-transformers)
- [ ] Add FastAPI backend
- [ ] Build Streamlit dashboard
- [ ] Add email notifications

---

## License

MIT License - For educational purposes