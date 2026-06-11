# Assumptions & Design Decisions

This document outlines all assumptions and design decisions made during MVP implementation.

---

## 1. Architecture Decisions

### 1.1 Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    CLI / Main Entry                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Config     │  │  Scraper    │  │  Reports    │    │
│  │  Loader     │  │  Module     │  │  Generator  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                 │                 │           │
│         ▼                 ▼                 ▼           │
│  ┌─────────────────────────────────────────────┐      │
│  │              Service Layer                    │      │
│  │  ┌─────────────┐  ┌─────────────┐             │      │
│  │  │  Scoring    │  │  Export     │             │      │
│  │  │  Service    │  │  Service    │             │      │
│  │  └──────┬──────┘  └──────┬──────┘             │      │
│  └─────────┼─────────────────┼─────────────────────┘      │
│            │                 │                          │
│            ▼                 ▼                          │
│  ┌─────────────────────────────────────────────┐      │
│  │           Data Layer (SQLite)                │      │
│  │  Jobs Table  |  Scores Table                │      │
│  └─────────────────────────────────────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Assumption:** Clean separation allows easy replacement of any layer.

### 1.2 SQLite for MVP

**Decision:** Use SQLite instead of PostgreSQL.

**Assumptions:**
- Single user access (no concurrent writes)
- < 100,000 job records expected
- No complex queries requiring advanced DB features
- Local storage is acceptable

**Limitation:** Not suitable for production with multiple users.

---

## 2. Configuration

### 2.1 JSON Configuration Format

**Assumption:** JSON is sufficient for profile configuration.

**Trade-offs:**
- ✅ Human-readable and editable
- ✅ No external dependencies
- ✅ Easy to version control
- ❌ No validation at load time (handled in Python)
- ❌ No schema enforcement

### 2.2 Profile Structure

**Assumptions:**
- Profile is single-user (no multi-profile support)
- Skills have proficiency levels (1-5 scale)
- Key skills are weighted more heavily in scoring

---

## 3. Job Scraping

### 3.1 Indeed Scraping

**Assumptions:**
- Indeed public search pages are accessible without authentication
- HTML structure is consistent across pages
- Rate limiting (2 seconds) is sufficient to avoid blocking

**Limitations:**
- Indeed may change HTML structure, breaking scraper
- No access to LinkedIn or other protected sources
- No access to premium job listings

### 3.2 Sample Jobs

**Assumption:** 10 sample jobs are sufficient for MVP testing.

**Sample job characteristics:**
- Diverse job titles matching target roles
- Varied locations (Jakarta, Bekasi, Karawang, Remote)
- Salary ranges within expected bounds (15M-28M IDR)
- Realistic descriptions with skill keywords

### 3.3 Data Freshness

**Assumption:** Job postings remain relevant for 30 days.

**Implementation:** `days_back` filter limits search to recent postings.

---

## 4. Job Scoring

### 4.1 Rule-Based Approach

**Decision:** Use keyword matching instead of ML embeddings.

**Rationale:**
- Simpler to implement and debug
- Deterministic and explainable
- No external model dependencies
- Fast execution

**Limitations:**
- Cannot capture semantic similarity
- Sensitive to keyword variations
- May miss similar skills with different names

### 4.2 Scoring Weights

Default weights based on importance:
| Component | Weight | Rationale |
|-----------|--------|----------|
| Skills | 40% | Most important for job fit |
| Title | 30% | Direct indicator of role |
| Location | 15% | Important but flexible |
| Salary | 10% | Range overlap is sufficient |
| Experience | 5% | Often not strictly enforced |

**Assumption:** Weights can be customized per user via config.

### 4.3 Skills Matching

**Matching strategies (in order of priority):**
1. Exact match (case-insensitive)
2. Alias match (using SKILL_ALIASES dictionary)
3. Compound skill match (all words present)

**Example aliases:**
```python
SKILL_ALIASES = {
    "sap": ["SAP", "SAP ECC", "SAP FI", "SAP CO", ...],
    "odoo": ["Odoo", "Odoo ERP", "OpenERP"],
    "bi": ["BI", "Business Intelligence", "Power BI", ...],
}
```

### 4.4 Score Labels

| Score Range | Label | Action |
|-------------|-------|--------|
| 90-100% | Excellent Match | High priority |
| 75-89% | Strong Match | Apply |
| 60-74% | Good Match | Research |
| 40-59% | Moderate Match | Consider |
| 0-39% | Low Match | Skip |

---

## 5. Data Storage

### 5.1 Database Schema

```sql
jobs (
    id, source, source_id, title, company, location,
    is_remote, salary_min, salary_max, salary_currency,
    employment_type, description, requirements, apply_url,
    posted_date, scraped_at, is_applied
)

job_scores (
    id, job_id, total_score, skills_score, title_score,
    location_score, salary_score, experience_score,
    matched_skills, missing_skills, scored_at
)
```

**Assumptions:**
- `source_id` is unique per source (for deduplication)
- `matched_skills` and `missing_skills` stored as comma-separated strings
- One score per job (upsert on re-score)

### 5.2 Data Retention

**Assumption:** Jobs remain relevant for 90 days.

**Implementation:** No automatic deletion in MVP (can be added in V2).

---

## 6. Reporting

### 6.1 Report Formats

| Format | Use Case | Dependencies |
|--------|----------|--------------|
| Text (.txt) | Quick viewing in terminal | None |
| HTML (.html) | Visual report in browser | CSS styling |
| Markdown (.md) | GitHub/README integration | None |
| CSV (.csv) | Data analysis in Excel | None |

**Assumption:** Plain text and HTML are sufficient for MVP.

### 6.2 Report Content

**Includes:**
- Summary statistics
- Top 20 job matches
- Score breakdowns
- Matched/missing skills
- Apply links

**Assumption:** 20 jobs per report is sufficient for review.

---

## 7. Performance

### 7.1 Scalability Limits

| Metric | MVP Limit | Rationale |
|--------|-----------|-----------|
| Jobs in DB | 100,000 | SQLite performance |
| Concurrent users | 1 | No connection pooling |
| Scraping rate | 30/hour | Rate limiting |
| Scoring time | <1s per job | Rule-based speed |

### 7.2 Memory Usage

**Assumption:** < 500MB RAM for typical usage.

**Estimates:**
- 1000 jobs ≈ 50MB
- Scores cached in memory during run
- Report generation ≈ 100MB peak

---

## 8. Security & Legal

### 8.1 Web Scraping

**Assumptions:**
- Personal/educational use only
- Rate limiting prevents server overload
- Respects robots.txt (implicitly)

**Risks:**
- IP blocking from Indeed
- Terms of Service violations
- HTML structure changes

### 8.2 Data Privacy

**Assumptions:**
- Local storage only (no cloud)
- No sensitive data stored
- Profile data is user-controlled

---

## 9. Future Considerations

### 9.1 V2 Enhancements

- PostgreSQL for multi-user support
- ML-based skill matching (sentence-transformers)
- More job sources (Glints, JobStreet, LinkedIn)
- Email notifications

### 9.2 Potential Issues

| Issue | Likelihood | Mitigation |
|-------|-------------|------------|
| Indeed blocks scraping | High | Fall back to sample data |
| HTML structure changes | High | Regular scraper maintenance |
| Performance degradation | Low | Index optimization |
| Data loss | Low | Backup strategy |

---

## 10. Testing Strategy

### 10.1 Test Scenarios

1. **Config Loading**
   - Valid JSON loads correctly
   - Invalid JSON raises appropriate error
   - Default values applied for missing fields

2. **Database Operations**
   - Jobs can be inserted and retrieved
   - Duplicate jobs are handled
   - Scores can be updated

3. **Scoring**
   - Jobs score between 0-100
   - Component scores sum to weighted total
   - Empty jobs get neutral scores

4. **Reports**
   - All report formats generate successfully
   - Output files are valid and readable

### 10.2 Sample Data Validation

- 10 sample jobs cover various scenarios
- Each job has different score range
- Skills include both matched and missing

---

*Last Updated: June 2026*