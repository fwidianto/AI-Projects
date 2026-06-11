# Running the AI Job Intelligence Platform on Your PC

This guide will walk you through setting up and running the MVP on your local machine.

---

## Step 1: Prerequisites

### Required Software
1. **Python 3.11 or higher** - [Download here](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   
2. **Git** - [Download here](https://git-scm.com/download)
   - For cloning the repository

### Verify Installation
Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
python --version
git --version
```

---

## Step 2: Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/fwidianto/AI-Projects.git
cd AI-Projects
```

Or if you already have the files, navigate to the project folder:

```bash
cd path/to/AI-Projects
```

---

## Step 3: Create Virtual Environment (Recommended)

Creating a virtual environment keeps your project dependencies isolated:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

---

## Step 4: Install Dependencies

```bash
pip install -r mvp_requirements.txt
```

This installs:
- `requests` - For web scraping
- `beautifulsoup4` - For parsing HTML
- `lxml` - HTML parser
- `pandas` - For data handling

---

## Step 5: Customize Your Profile

Edit the file `config/profile.json` with your information:

```json
{
  "profile": {
    "name": "Your Name Here",
    "email": "your.email@example.com",
    "headline": "Your Professional Headline",
    "target_roles": [
      "ERP Analyst",
      "Business Analyst",
      "Operations Analyst"
    ],
    "preferred_locations": [
      "Jakarta",
      "Remote"
    ],
    "salary_expectations": {
      "min": 15000000,
      "max": 25000000
    },
    "skills": [
      {"name": "SAP", "proficiency": 5, "is_key_skill": true},
      {"name": "SQL", "proficiency": 4, "is_key_skill": true}
    ]
  }
}
```

---

## Step 6: Run the Application

### Option A: Quick Demo (Use Sample Jobs)
No web scraping needed - uses pre-loaded sample jobs:

```bash
python main.py --setup
python main.py --scrape --use-sample
python main.py --score
python main.py --report
```

### Option B: Run Everything at Once
```bash
python main.py --all
```

### Option C: Interactive Mode
```bash
python main.py --profile      # View your profile
python main.py --stats        # View database stats
python main.py --scrape --use-sample   # Scrape jobs
python main.py --score        # Score jobs
python main.py --report       # Generate reports
```

---

## Step 7: View Your Results

After running, check the `data/` folder:

```
data/
├── jobs.db              # SQLite database (open with DB Browser)
├── job_report.txt       # Plain text report
├── job_report.html      # Styled HTML report (open in browser!)
├── job_report.md        # Markdown report
├── jobs_export.csv      # Full data export (open in Excel)
└── jobs_summary.csv     # Summary (open in Excel)
```

### View HTML Report
```bash
# Windows
start data\job_report.html

# Mac
open data/job_report.html

# Linux
xdg-open data/job_report.html
```

### View in Excel/Google Sheets
Open `data/jobs_export.csv` or `data/jobs_summary.csv` in Excel or Google Sheets.

---

## Step 8: Customize Your Search

Edit `config/profile.json` to change:

### Change Target Roles
```json
"target_roles": ["Data Analyst", "BI Analyst", "Financial Analyst"]
```

### Change Locations
```json
"preferred_locations": ["Bekasi", "Karawang", "Remote"]
```

### Change Salary Expectations
```json
"salary_expectations": {
  "min": 18000000,
  "max": 30000000
}
```

### Adjust Scoring Weights
```json
"scoring_weights": {
  "skills_match": 0.50,      # Increase if skills are most important
  "title_match": 0.20,      # Decrease if title doesn't matter
  "location_match": 0.10,
  "salary_match": 0.10,
  "experience_match": 0.10
}
```

---

## Troubleshooting

### "python not found" or "python is not recognized"
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python`

### "Module not found" errors
- Make sure you activated the virtual environment
- Run `pip install -r mvp_requirements.txt` again

### Database errors
- Delete `data/jobs.db` and run `--setup` again

### Scraping issues
- Use `--use-sample` flag to skip web scraping
- Check your internet connection

---

## Common Commands Cheatsheet

| Command | Description |
|---------|-------------|
| `python main.py --setup` | Initialize database with sample data |
| `python main.py --scrape --use-sample` | Load sample jobs |
| `python main.py --scrape` | Scrape from Indeed (requires internet) |
| `python main.py --score` | Score all jobs against your profile |
| `python main.py --report` | Generate all reports |
| `python main.py --all` | Run everything |
| `python main.py --profile` | Show your profile |
| `python main.py --stats` | Show database statistics |
| `python main.py --help` | Show all options |

---

## Next Steps After MVP

Want to do more? Check out:

1. **Add more job sources** - Glints, JobStreet (V2 feature)
2. **Build dashboard** - Streamlit web interface (V2 feature)
3. **Add API** - FastAPI backend (V2 feature)
4. **ML scoring** - Use AI embeddings for better matching (V3 feature)

---

## Need Help?

If you encounter issues:
1. Check the `ASSUMPTIONS.md` file for design decisions
2. Delete `data/jobs.db` and start fresh
3. Create an issue on GitHub

Happy job hunting! 🎯