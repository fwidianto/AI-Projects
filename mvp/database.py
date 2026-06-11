"""
MVP SQLite Database Module

Manages SQLite database for job storage and retrieval.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os


@dataclass
class Job:
    """Job dataclass."""
    id: Optional[int] = None
    source: str = ""
    source_id: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "IDR"
    employment_type: str = ""
    description: str = ""
    requirements: str = ""
    apply_url: str = ""
    posted_date: Optional[str] = None
    scraped_at: Optional[str] = None
    is_applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "is_remote": self.is_remote,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "salary_display": self.salary_display,
            "employment_type": self.employment_type,
            "description": self.description[:200] + "..." if len(self.description) > 200 else self.description,
            "requirements": self.requirements,
            "apply_url": self.apply_url,
            "posted_date": self.posted_date,
            "scraped_at": self.scraped_at,
            "is_applied": self.is_applied,
        }
    
    @property
    def salary_display(self) -> str:
        """Get formatted salary display."""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min/1_000_000:.0f}M - {self.salary_max/1_000_000:.0f}M {self.salary_currency}"
        elif self.salary_min:
            return f"{self.salary_min/1_000_000:.0f}M+ {self.salary_currency}"
        return "Not disclosed"


@dataclass
class JobScore:
    """Job score dataclass."""
    id: Optional[int] = None
    job_id: int = 0
    total_score: float = 0.0
    skills_score: float = 0.0
    title_score: float = 0.0
    location_score: float = 0.0
    salary_score: float = 0.0
    experience_score: float = 0.0
    matched_skills: str = ""
    missing_skills: str = ""
    scored_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "total_score": round(self.total_score, 1),
            "skills_score": round(self.skills_score, 1),
            "title_score": round(self.title_score, 1),
            "location_score": round(self.location_score, 1),
            "salary_score": round(self.salary_score, 1),
            "experience_score": round(self.experience_score, 1),
            "matched_skills": self.matched_skills.split(",") if self.matched_skills else [],
            "missing_skills": self.missing_skills.split(",") if self.missing_skills else [],
            "score_label": self.score_label,
            "scored_at": self.scored_at,
        }
    
    @property
    def score_label(self) -> str:
        """Get human-readable score label."""
        if self.total_score >= 90:
            return "Excellent Match"
        elif self.total_score >= 75:
            return "Strong Match"
        elif self.total_score >= 60:
            return "Good Match"
        elif self.total_score >= 40:
            return "Moderate Match"
        return "Low Match"


class Database:
    """
    SQLite database manager for job intelligence.
    
    Assumptions:
        - Single user, local storage
        - SQLite is sufficient for MVP scale (< 100K jobs)
        - Data persistence between sessions is required
        - No concurrent access from multiple processes
    """
    
    def __init__(self, db_path: str = "data/jobs.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                is_remote INTEGER DEFAULT 0,
                salary_min INTEGER,
                salary_max INTEGER,
                salary_currency TEXT DEFAULT 'IDR',
                employment_type TEXT,
                description TEXT,
                requirements TEXT,
                apply_url TEXT,
                posted_date TEXT,
                scraped_at TEXT NOT NULL,
                is_applied INTEGER DEFAULT 0,
                UNIQUE(source, source_id)
            )
        """)
        
        # Job scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                total_score REAL NOT NULL,
                skills_score REAL NOT NULL,
                title_score REAL NOT NULL,
                location_score REAL NOT NULL,
                salary_score REAL NOT NULL,
                experience_score REAL NOT NULL,
                matched_skills TEXT,
                missing_skills TEXT,
                scored_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                UNIQUE(job_id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_posted ON jobs(posted_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_job ON job_scores(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_total ON job_scores(total_score)")
        
        conn.commit()
        conn.close()
    
    def insert_job(self, job: Job) -> int:
        """
        Insert a job into the database.
        
        Args:
            job: Job object to insert
            
        Returns:
            int: Job ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO jobs (
                source, source_id, title, company, location, is_remote,
                salary_min, salary_max, salary_currency, employment_type,
                description, requirements, apply_url, posted_date, scraped_at, is_applied
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.source, job.source_id, job.title, job.company, job.location,
            1 if job.is_remote else 0, job.salary_min, job.salary_max,
            job.salary_currency, job.employment_type, job.description,
            job.requirements, job.apply_url, job.posted_date, now, 
            1 if job.is_applied else 0
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def insert_jobs_batch(self, jobs: List[Job]) -> int:
        """
        Insert multiple jobs in a single transaction.
        
        Args:
            jobs: List of Job objects
            
        Returns:
            int: Number of jobs inserted
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        count = 0
        
        for job in jobs:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO jobs (
                        source, source_id, title, company, location, is_remote,
                        salary_min, salary_max, salary_currency, employment_type,
                        description, requirements, apply_url, posted_date, scraped_at, is_applied
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.source, job.source_id, job.title, job.company, job.location,
                    1 if job.is_remote else 0, job.salary_min, job.salary_max,
                    job.salary_currency, job.employment_type, job.description,
                    job.requirements, job.apply_url, job.posted_date, now,
                    1 if job.is_applied else 0
                ))
                count += cursor.rowcount
            except sqlite3.Error:
                continue
        
        conn.commit()
        conn.close()
        
        return count
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Get a job by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_job(row)
        return None
    
    def get_all_jobs(self, limit: int = 100, offset: int = 0) -> List[Job]:
        """Get all jobs with pagination."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs 
            ORDER BY scraped_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_job(row) for row in rows]
    
    def search_jobs(self, query: str = "", location: str = "") -> List[Job]:
        """
        Search jobs by query and/or location.
        
        Args:
            query: Search query (matches title, company, description)
            location: Location filter
            
        Returns:
            List of matching jobs
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM jobs WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            q = f"%{query}%"
            params.extend([q, q, q])
        
        if location:
            sql += " AND (location LIKE ? OR is_remote = 1)"
            params.append(f"%{location}%")
        
        sql += " ORDER BY scraped_at DESC LIMIT 100"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_job(row) for row in rows]
    
    def insert_score(self, score: JobScore) -> int:
        """Insert or update a job score."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO job_scores (
                job_id, total_score, skills_score, title_score, 
                location_score, salary_score, experience_score,
                matched_skills, missing_skills, scored_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            score.job_id, score.total_score, score.skills_score,
            score.title_score, score.location_score, score.salary_score,
            score.experience_score, score.matched_skills, score.missing_skills, now
        ))
        
        score_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return score_id
    
    def get_jobs_with_scores(self, min_score: float = 0, limit: int = 50) -> List[Dict]:
        """
        Get jobs with their scores.
        
        Args:
            min_score: Minimum total score filter
            limit: Maximum results
            
        Returns:
            List of job dictionaries with scores
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT j.*, s.total_score, s.skills_score, s.title_score,
                   s.location_score, s.salary_score, s.experience_score,
                   s.matched_skills, s.missing_skills, s.score_label
            FROM jobs j
            JOIN (
                SELECT job_id, total_score, skills_score, title_score,
                       location_score, salary_score, experience_score,
                       matched_skills, missing_skills,
                       CASE 
                           WHEN total_score >= 90 THEN 'Excellent Match'
                           WHEN total_score >= 75 THEN 'Strong Match'
                           WHEN total_score >= 60 THEN 'Good Match'
                           WHEN total_score >= 40 THEN 'Moderate Match'
                           ELSE 'Low Match'
                       END as score_label
                FROM job_scores
                WHERE total_score >= ?
            ) s ON j.id = s.job_id
            ORDER BY s.total_score DESC
            LIMIT ?
        """, (min_score, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "job": self._row_to_job(row).to_dict(),
                "score": {
                    "total_score": round(row["total_score"], 1),
                    "skills_score": round(row["skills_score"], 1),
                    "title_score": round(row["title_score"], 1),
                    "location_score": round(row["location_score"], 1),
                    "salary_score": round(row["salary_score"], 1),
                    "experience_score": round(row["experience_score"], 1),
                    "matched_skills": row["matched_skills"].split(",") if row["matched_skills"] else [],
                    "missing_skills": row["missing_skills"].split(",") if row["missing_skills"] else [],
                    "score_label": row["score_label"],
                }
            })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        stats["total_jobs"] = cursor.fetchone()["count"]
        
        # Jobs with scores
        cursor.execute("SELECT COUNT(*) as count FROM job_scores")
        stats["scored_jobs"] = cursor.fetchone()["count"]
        
        # Applied jobs
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE is_applied = 1")
        stats["applied_jobs"] = cursor.fetchone()["count"]
        
        # Jobs by source
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM jobs 
            GROUP BY source
        """)
        stats["by_source"] = [{"source": r["source"], "count": r["count"]} for r in cursor.fetchall()]
        
        # Score distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN total_score >= 90 THEN '90+'
                    WHEN total_score >= 75 THEN '75-89'
                    WHEN total_score >= 60 THEN '60-74'
                    WHEN total_score >= 40 THEN '40-59'
                    ELSE '<40'
                END as range,
                COUNT(*) as count
            FROM job_scores
            GROUP BY range
            ORDER BY range
        """)
        stats["score_distribution"] = [{"range": r["range"], "count": r["count"]} for r in cursor.fetchall()]
        
        conn.close()
        
        return stats
    
    def _row_to_job(self, row: sqlite3.Row) -> Job:
        """Convert database row to Job object."""
        return Job(
            id=row["id"],
            source=row["source"],
            source_id=row["source_id"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            is_remote=bool(row["is_remote"]),
            salary_min=row["salary_min"],
            salary_max=row["salary_max"],
            salary_currency=row["salary_currency"],
            employment_type=row["employment_type"],
            description=row["description"],
            requirements=row["requirements"],
            apply_url=row["apply_url"],
            posted_date=row["posted_date"],
            scraped_at=row["scraped_at"],
            is_applied=bool(row["is_applied"]),
        )