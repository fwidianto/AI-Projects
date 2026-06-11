"""
MVP CSV Export Module

Exports job data and scores to CSV format.

Assumptions:
    - CSV is sufficient for MVP reporting
    - UTF-8 encoding for international characters
    - Standard CSV format (comma-separated with quotes)
"""

import csv
import os
from typing import List, Dict, Any
from datetime import datetime

from mvp.database import Job


def _get_job_dict(item) -> Dict[str, Any]:
    """Convert ScoringResult or dict to job dict."""
    if hasattr(item, 'job'):
        job = item.job
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "is_remote": job.is_remote,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_display": job.salary_display,
            "employment_type": job.employment_type,
            "description": job.description,
            "requirements": job.requirements,
            "apply_url": job.apply_url,
            "posted_date": job.posted_date,
            "source": job.source,
        }
    elif isinstance(item, dict):
        return item.get("job", item)
    else:
        return item


def _get_score_dict(item) -> Dict[str, Any]:
    """Convert ScoringResult or dict to score dict."""
    if hasattr(item, 'score'):
        score = item.score
        return {
            "total_score": score.total_score,
            "skills_score": score.skills_score,
            "title_score": score.title_score,
            "location_score": score.location_score,
            "salary_score": score.salary_score,
            "experience_score": score.experience_score,
            "score_label": score.score_label,
            "matched_skills": score.matched_skills.split(',') if isinstance(score.matched_skills, str) else score.matched_skills,
            "missing_skills": score.missing_skills.split(',') if isinstance(score.missing_skills, str) else score.missing_skills,
        }
    elif isinstance(item, dict):
        return item.get("score", {})
    else:
        return {}


def export_jobs_to_csv(
    jobs: List[Dict[str, Any]],
    output_path: str = "data/jobs_export.csv",
) -> str:
    """
    Export jobs to CSV file.
    
    Args:
        jobs: List of ScoringResult objects or dicts with job/score keys
        output_path: Path for output CSV file
        
    Returns:
        Path to created CSV file
        
    Assumptions:
        - Jobs dictionary has standard structure
        - Optional score data may be present
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    # Define fieldnames
    fieldnames = [
        "id",
        "title",
        "company",
        "location",
        "is_remote",
        "salary_min",
        "salary_max",
        "salary_display",
        "employment_type",
        "description",
        "requirements",
        "apply_url",
        "posted_date",
        "source",
        # Score fields (may be empty)
        "total_score",
        "skills_score",
        "title_score",
        "location_score",
        "salary_score",
        "experience_score",
        "score_label",
        "matched_skills",
        "missing_skills",
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        
        for item in jobs:
            job = _get_job_dict(item)
            score = _get_score_dict(item)
            
            matched = score.get("matched_skills", [])
            if isinstance(matched, list):
                matched = ", ".join(matched)
            
            missing = score.get("missing_skills", [])
            if isinstance(missing, list):
                missing = ", ".join(missing)
            
            row = {
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "is_remote": "Yes" if job.get("is_remote") else "No",
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "salary_display": job.get("salary_display"),
                "employment_type": job.get("employment_type"),
                "description": job.get("description"),
                "requirements": job.get("requirements"),
                "apply_url": job.get("apply_url"),
                "posted_date": job.get("posted_date"),
                "source": job.get("source"),
                # Score fields
                "total_score": score.get("total_score"),
                "skills_score": score.get("skills_score"),
                "title_score": score.get("title_score"),
                "location_score": score.get("location_score"),
                "salary_score": score.get("salary_score"),
                "experience_score": score.get("experience_score"),
                "score_label": score.get("score_label"),
                "matched_skills": matched,
                "missing_skills": missing,
            }
            
            writer.writerow(row)
    
    return output_path


def export_summary_csv(
    jobs: List[Dict[str, Any]],
    output_path: str = "data/jobs_summary.csv",
) -> str:
    """
    Export a summary view of jobs (fewer columns).
    
    Args:
        jobs: List of ScoringResult objects or dicts with job/score keys
        output_path: Path for output CSV file
        
    Returns:
        Path to created CSV file
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    fieldnames = [
        "rank",
        "title",
        "company",
        "location",
        "salary_display",
        "total_score",
        "score_label",
        "top_skills",
        "apply_url",
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for rank, item in enumerate(jobs, 1):
            job = _get_job_dict(item)
            score = _get_score_dict(item)
            
            matched = score.get("matched_skills", [])
            if isinstance(matched, str):
                matched = matched.split(',')
            if isinstance(matched, list):
                matched = [s.strip() for s in matched]
            
            row = {
                "rank": rank,
                "title": job.get("title"),
                "company": job.get("company"),
                "location": "Remote" if job.get("is_remote") else job.get("location"),
                "salary_display": job.get("salary_display"),
                "total_score": f"{score.get('total_score', 0):.1f}%",
                "score_label": score.get("score_label", ""),
                "top_skills": ", ".join(matched[:3]) if matched else "",
                "apply_url": job.get("apply_url", ""),
            }
            
            writer.writerow(row)
    
    return output_path


def export_profile_csv(
    profile_data: Dict[str, Any],
    output_path: str = "data/profile_export.csv",
) -> str:
    """
    Export profile data to CSV.
    
    Args:
        profile_data: Profile dictionary
        output_path: Path for output CSV file
        
    Returns:
        Path to created CSV file
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header info
        writer.writerow(["Field", "Value"])
        writer.writerow(["Name", profile_data.get("name", "")])
        writer.writerow(["Email", profile_data.get("email", "")])
        writer.writerow(["Headline", profile_data.get("headline", "")])
        writer.writerow(["Experience (Years)", profile_data.get("experience_years", "")])
        
        # Target roles
        roles = profile_data.get("target_roles", [])
        writer.writerow(["Target Roles", ", ".join(roles) if roles else ""])
        
        # Preferred locations
        locations = profile_data.get("preferred_locations", [])
        writer.writerow(["Preferred Locations", ", ".join(locations) if locations else ""])
        
        # Salary expectations
        salary = profile_data.get("salary_expectations", {})
        if salary:
            writer.writerow([
                "Salary Expectations",
                f"{salary.get('min', 0)/1_000_000:.0f}M - {salary.get('max', 0)/1_000_000:.0f}M {salary.get('currency', 'IDR')}"
            ])
        
        # Skills
        skills = profile_data.get("skills", [])
        if skills:
            writer.writerow(["Skills", ""])
            writer.writerow(["Skill Name", "Proficiency", "Key Skill"])
            for skill in skills:
                writer.writerow([
                    skill.get("name", ""),
                    skill.get("proficiency", ""),
                    "Yes" if skill.get("is_key_skill") else "No"
                ])
    
    return output_path