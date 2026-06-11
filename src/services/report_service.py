"""Report generation service."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from io import BytesIO
import json

from sqlalchemy.orm import Session, joinedload

from src.models.job import Job
from src.models.profile import Profile
from src.models.score import JobScore, Recommendation
from src.utils.logger import get_logger
from src.utils.helpers import format_currency, time_ago

logger = get_logger(__name__)


class ReportService:
    """Service for generating job reports."""

    def __init__(self, db: Session):
        """Initialize report service with database session."""
        self.db = db

    def generate_daily_digest(
        self,
        profile_id: int,
        days_back: int = 1,
    ) -> Dict[str, Any]:
        """
        Generate daily job digest.
        
        Args:
            profile_id: Profile ID
            days_back: Number of days to look back
            
        Returns:
            Dict with digest data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get recent jobs
        recent_jobs = (
            self.db.query(Job)
            .filter(Job.scraped_at >= cutoff_date)
            .filter(Job.is_active == True)
            .order_by(Job.scraped_at.desc())
            .all()
        )
        
        # Get scores for these jobs
        job_ids = [j.id for j in recent_jobs]
        scores = (
            self.db.query(JobScore)
            .filter(JobScore.profile_id == profile_id)
            .filter(JobScore.job_id.in_(job_ids))
            .all()
        )
        
        scores_dict = {s.job_id: s for s in scores}
        
        # Format job data with scores
        jobs_with_scores = []
        for job in recent_jobs:
            score = scores_dict.get(job.id)
            if score:
                jobs_with_scores.append({
                    "job": job.to_dict(),
                    "score": score.total_score,
                    "score_label": score.score_label,
                    "matched_skills": score.matched_skills_list,
                })
        
        # Sort by score
        jobs_with_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Get top picks
        top_picks = jobs_with_scores[:5]
        
        return {
            "profile_id": profile_id,
            "generated_at": datetime.utcnow().isoformat(),
            "period": f"Last {days_back} day(s)",
            "total_new_jobs": len(recent_jobs),
            "total_scored": len(jobs_with_scores),
            "top_picks": top_picks,
            "all_jobs": jobs_with_scores,
        }

    def generate_weekly_report(
        self,
        profile_id: int,
    ) -> Dict[str, Any]:
        """
        Generate weekly job report.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Dict with report data
        """
        profile = self.db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Get all active jobs
        all_jobs = (
            self.db.query(Job)
            .filter(Job.is_active == True)
            .all()
        )
        
        # Get all scores for this profile
        scores = (
            self.db.query(JobScore)
            .filter(JobScore.profile_id == profile_id)
            .all()
        )
        
        scores_dict = {s.job_id: s for s in scores}
        
        # Categorize jobs
        high_matches = []  # 80+
        medium_matches = []  # 60-80
        low_matches = []  # <60
        
        for job in all_jobs:
            score = scores_dict.get(job.id)
            if not score:
                continue
            
            job_data = {
                "job": job.to_dict(),
                "score": score.total_score,
                "score_label": score.score_label,
                "matched_skills": score.matched_skills_list,
                "missing_skills": score.missing_skills_list,
            }
            
            if score.total_score >= 80:
                high_matches.append(job_data)
            elif score.total_score >= 60:
                medium_matches.append(job_data)
            else:
                low_matches.append(job_data)
        
        # Sort each category by score
        high_matches.sort(key=lambda x: x["score"], reverse=True)
        medium_matches.sort(key=lambda x: x["score"], reverse=True)
        low_matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Stats
        applied_count = sum(1 for j in all_jobs if j.is_applied)
        avg_score = sum(s.total_score for s in scores) / len(scores) if scores else 0
        
        return {
            "profile": profile.to_dict(),
            "generated_at": datetime.utcnow().isoformat(),
            "period": "Last 7 days",
            "summary": {
                "total_jobs_tracked": len(all_jobs),
                "total_scored": len(scores),
                "high_matches": len(high_matches),
                "medium_matches": len(medium_matches),
                "low_matches": len(low_matches),
                "applied_jobs": applied_count,
                "average_score": round(avg_score, 1),
            },
            "high_priority": high_matches[:10],
            "medium_priority": medium_matches[:10],
            "recommendations": self._generate_recommendations_summary(profile_id),
        }

    def _generate_recommendations_summary(self, profile_id: int) -> List[Dict]:
        """Generate summary of recommendations."""
        recs = (
            self.db.query(Recommendation)
            .filter(Recommendation.profile_id == profile_id)
            .filter(Recommendation.is_dismissed == False)
            .order_by(Recommendation.priority, Recommendation.created_at.desc())
            .limit(5)
            .all()
        )
        
        return [
            {
                "type": r.recommendation_type,
                "priority": r.priority_label,
                "reason": r.reason,
                "job_id": r.job_id,
            }
            for r in recs
        ]

    def generate_pdf_report(
        self,
        profile_id: int,
        report_type: str = "weekly",
    ) -> BytesIO:
        """
        Generate PDF report.
        
        Args:
            profile_id: Profile ID
            report_type: Type of report (daily, weekly)
            
        Returns:
            BytesIO: PDF file content
        """
        try:
            from weasyprint import HTML, CSS
            
            if report_type == "daily":
                data = self.generate_daily_digest(profile_id)
            else:
                data = self.generate_weekly_report(profile_id)
            
            html_content = self._generate_html_report(data, report_type)
            
            pdf_buffer = BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            
            return pdf_buffer
            
        except ImportError:
            logger.warning("WeasyPrint not installed, returning empty PDF")
            return BytesIO()

    def _generate_html_report(self, data: Dict, report_type: str) -> str:
        """Generate HTML content for PDF report."""
        title = "Daily Job Digest" if report_type == "daily" else "Weekly Job Report"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .job-card {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .score {{ font-weight: bold; color: #007bff; }}
                .skills {{ color: #28a745; }}
                .missing {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #007bff; color: white; }}
                .high {{ border-left: 4px solid #28a745; }}
                .medium {{ border-left: 4px solid #ffc107; }}
                .low {{ border-left: 4px solid #dc3545; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated: {data.get('generated_at', '')}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total Jobs:</strong> {data.get('summary', {}).get('total_jobs_tracked', data.get('total_new_jobs', 0))}</p>
                <p><strong>High Matches:</strong> {data.get('summary', {}).get('high_matches', len(data.get('high_priority', [])))}</p>
                <p><strong>Medium Matches:</strong> {data.get('summary', {}).get('medium_matches', len(data.get('medium_priority', [])))}</p>
                <p><strong>Applied:</strong> {data.get('summary', {}).get('applied_jobs', 0)}</p>
            </div>
            
            <h2>Top Job Matches</h2>
        """
        
        for job_data in data.get('high_priority', data.get('top_picks', []))[:10]:
            job = job_data.get('job', {})
            html += f"""
            <div class="job-card high">
                <h3>{job.get('title', 'N/A')} at {job.get('company', 'N/A')}</h3>
                <p><strong>Location:</strong> {job.get('location', 'N/A')} | 
                   <strong>Salary:</strong> {job.get('salary_display', 'N/A')}</p>
                <p><strong>Match Score:</strong> <span class="score">{job_data.get('score', 0):.1f}%</span> 
                   ({job_data.get('score_label', 'N/A')})</p>
                <p class="skills"><strong>Matched Skills:</strong> {', '.join(job_data.get('matched_skills', []))}</p>
                <p><a href="{job.get('apply_url', '#')}">Apply Here</a></p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html

    def generate_csv_export(
        self,
        profile_id: int,
        min_score: float = 0,
    ) -> str:
        """
        Generate CSV export of jobs.
        
        Args:
            profile_id: Profile ID
            min_score: Minimum score threshold
            
        Returns:
            str: CSV content
        """
        scores = (
            self.db.query(JobScore)
            .filter(JobScore.profile_id == profile_id)
            .filter(JobScore.total_score >= min_score)
            .order_by(JobScore.total_score.desc())
            .all()
        )
        
        lines = [
            "Job ID,Title,Company,Location,Salary,Score,Matched Skills,Missing Skills,Apply URL,Posted Date"
        ]
        
        for score in scores:
            job = self.db.query(Job).filter(Job.id == score.job_id).first()
            if not job:
                continue
            
            line = (
                f"{job.id},"
                f'"{job.title}",'
                f'"{job.company}",'
                f'"{job.location or ""}",'
                f'"{job.salary_range_display}",'
                f"{score.total_score:.1f},"
                f'"{', '.join(score.matched_skills_list)}",'
                f'"{', '.join(score.missing_skills_list)}",'
                f'"{job.apply_url or ""}",'
                f'"{job.posted_date.strftime("%Y-%m-%d") if job.posted_date else ""}"'
            )
            lines.append(line)
        
        return "\n".join(lines)

    def get_dashboard_stats(self, profile_id: int) -> Dict[str, Any]:
        """Get dashboard statistics."""
        all_jobs = self.db.query(Job).filter(Job.is_active == True).all()
        all_scores = self.db.query(JobScore).filter(JobScore.profile_id == profile_id).all()
        applied = self.db.query(Job).filter(Job.is_active == True, Job.is_applied == True).count()
        
        # Score distribution
        score_ranges = {
            "90+": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "50-59": 0,
            "<50": 0,
        }
        
        for score in all_scores:
            if score.total_score >= 90:
                score_ranges["90+"] += 1
            elif score.total_score >= 80:
                score_ranges["80-89"] += 1
            elif score.total_score >= 70:
                score_ranges["70-79"] += 1
            elif score.total_score >= 60:
                score_ranges["60-69"] += 1
            elif score.total_score >= 50:
                score_ranges["50-59"] += 1
            else:
                score_ranges["<50"] += 1
        
        # Skills coverage
        all_job_skills = set()
        profile_skills_set = set()
        
        for job in all_jobs:
            for skill in job.skills:
                all_job_skills.add(skill.skill_name)
        
        # Jobs by location
        location_counts = {}
        for job in all_jobs:
            loc = job.location or "Unknown"
            loc = "Remote" if job.is_remote else loc
            location_counts[loc] = location_counts.get(loc, 0) + 1
        
        return {
            "total_jobs": len(all_jobs),
            "total_scores": len(all_scores),
            "applied": applied,
            "avg_score": sum(s.total_score for s in all_scores) / len(all_scores) if all_scores else 0,
            "score_distribution": score_ranges,
            "location_breakdown": location_counts,
            "top_skills_in_demand": list(all_job_skills)[:20],
        }