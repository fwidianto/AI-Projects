"""
MVP Report Generator Module

Generates simple text and HTML reports for job search results.

Assumptions:
    - Plain text reports are sufficient for MVP
    - HTML reports can be viewed in browser
    - No PDF generation for MVP (requires additional dependencies)
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from mvp.config_loader import Profile


def generate_text_report(
    jobs: List[Dict[str, Any]],
    profile: Profile,
    output_path: str = "data/job_report.txt",
) -> str:
    """
    Generate a simple text report.
    
    Args:
        jobs: List of ScoringResult objects or dicts with job/score keys
        profile: User profile
        output_path: Path for output file
        
    Returns:
        Path to created report
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("AI JOB INTELLIGENCE - JOB MATCH REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Profile: {profile.name}")
    lines.append(f"Target Roles: {', '.join(profile.target_roles[:5])}")
    lines.append(f"Locations: {', '.join(profile.preferred_locations)}")
    lines.append("")
    
    # Summary
    lines.append("-" * 80)
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Jobs Found: {len(jobs)}")
    
    if jobs:
        # Handle both ScoringResult objects and dicts
        scores = []
        for item in jobs:
            if hasattr(item, 'score'):
                scores.append(item.score.total_score)
            elif isinstance(item, dict) and "score" in item:
                scores.append(item["score"]["total_score"])
        
        if scores:
            lines.append(f"Average Match Score: {sum(scores) / len(scores):.1f}%")
            lines.append(f"Highest Match: {max(scores):.1f}%")
            lines.append(f"Lowest Match: {min(scores):.1f}%")
            
            # Count by label
            labels = {}
            for item in jobs:
                if hasattr(item, 'score'):
                    label = item.score.score_label
                elif isinstance(item, dict):
                    label = item.get("score", {}).get("score_label", "Unknown")
                else:
                    label = "Unknown"
                labels[label] = labels.get(label, 0) + 1
            
            lines.append("")
            lines.append("Score Distribution:")
            for label in ["Excellent Match", "Strong Match", "Good Match", "Moderate Match", "Low Match"]:
                if label in labels:
                    lines.append(f"  {label}: {labels[label]}")
    
    lines.append("")
    lines.append("-" * 80)
    lines.append("TOP JOB MATCHES")
    lines.append("-" * 80)
    
    # Top 20 jobs
    for rank, item in enumerate(jobs[:20], 1):
        if hasattr(item, 'job'):
            job = item.job
            score = item.score
        else:
            job = item.get("job", {})
            score = item.get("score", {})
        
        lines.append("")
        lines.append(f"{rank}. {job.title if hasattr(job, 'title') else job.get('title', 'N/A')}")
        lines.append(f"   Company: {job.company if hasattr(job, 'company') else job.get('company', 'N/A')}")
        lines.append(f"   Location: {'Remote' if (job.is_remote if hasattr(job, 'is_remote') else job.get('is_remote')) else (job.location if hasattr(job, 'location') else job.get('location', 'N/A'))}")
        
        # Handle both object and dict access
        total_score = score.total_score if hasattr(score, 'total_score') else score.get('total_score', 0)
        score_label = score.score_label if hasattr(score, 'score_label') else score.get('score_label', 'N/A')
        lines.append(f"   Match Score: {total_score:.1f}% ({score_label})")
        
        matched = score.matched_skills if hasattr(score, 'matched_skills') else score.get('matched_skills', [])
        if isinstance(matched, str):
            matched = matched.split(',') if matched else []
        if matched:
            lines.append(f"   Matched Skills: {', '.join(matched[:5])}")
        
        missing = score.missing_skills if hasattr(score, 'missing_skills') else score.get('missing_skills', [])
        if isinstance(missing, str):
            missing = missing.split(',') if missing else []
        if missing:
            lines.append(f"   Missing Skills: {', '.join(missing[:3])}")
        
        # Handle salary display
        if hasattr(job, 'salary_display'):
            salary = job.salary_display
        elif hasattr(job, 'salary_min') and hasattr(job, 'salary_max'):
            if job.salary_min and job.salary_max:
                salary = f"{job.salary_min/1_000_000:.0f}M - {job.salary_max/1_000_000:.0f}M IDR"
            else:
                salary = "Not disclosed"
        else:
            salary = job.get("salary_display", "Not disclosed")
        lines.append(f"   Salary: {salary}")
        
        # Handle apply URL
        apply_url = job.apply_url if hasattr(job, 'apply_url') else job.get('apply_url')
        if apply_url:
            lines.append(f"   Apply: {apply_url[:70]}...")
    
    # Footer
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    # Write to file
    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def generate_html_report(
    jobs: List[Dict[str, Any]],
    profile: Profile,
    output_path: str = "data/job_report.html",
) -> str:
    """
    Generate an HTML report with styling.
    
    Args:
        jobs: List of job dictionaries with scores
        profile: User profile
        output_path: Path for output file
        
    Returns:
        Path to created report
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    # Calculate stats - handle both ScoringResult objects and dicts
    total_jobs = len(jobs)
    scores = []
    for item in jobs:
        if hasattr(item, 'score'):
            scores.append(item.score.total_score)
        elif isinstance(item, dict) and "score" in item:
            scores.append(item["score"]["total_score"])
    
    avg_score = sum(scores) / len(scores) if scores else 0
    high_matches = len([s for s in scores if s >= 75])
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Match Report - {profile.name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header .meta {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        .filters {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .filters span {{
            display: inline-block;
            background: #e8e8e8;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 3px;
            font-size: 0.85em;
        }}
        .job-list {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        .job-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .job-card.high {{ border-left-color: #28a745; }}
        .job-card.medium {{ border-left-color: #ffc107; }}
        .job-card.low {{ border-left-color: #dc3545; }}
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        .job-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin: 0;
        }}
        .job-company {{
            color: #666;
            font-size: 0.95em;
        }}
        .score-badge {{
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            white-space: nowrap;
        }}
        .score-badge.excellent {{ background: #28a745; }}
        .score-badge.strong {{ background: #17a2b8; }}
        .score-badge.good {{ background: #ffc107; color: #333; }}
        .score-badge.moderate {{ background: #fd7e14; }}
        .score-badge.low {{ background: #dc3545; }}
        .job-meta {{
            display: flex;
            gap: 20px;
            color: #666;
            font-size: 0.9em;
            margin: 10px 0;
        }}
        .skills {{
            margin-top: 10px;
        }}
        .skill-tag {{
            display: inline-block;
            background: #e8f5e9;
            color: #2e7d32;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            margin: 2px;
        }}
        .skill-tag.missing {{
            background: #ffebee;
            color: #c62828;
        }}
        .job-actions {{
            margin-top: 15px;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9em;
        }}
        .btn:hover {{
            background: #5568d3;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.85em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Job Match Report</h1>
        <div class="meta">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
            Profile: {profile.name} | 
            Target: {', '.join(profile.target_roles[:3])}
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="value">{total_jobs}</div>
            <div class="label">Jobs Found</div>
        </div>
        <div class="stat-card">
            <div class="value">{avg_score:.1f}%</div>
            <div class="label">Avg Match</div>
        </div>
        <div class="stat-card">
            <div class="value">{high_matches}</div>
            <div class="label">High Matches (75%+)</div>
        </div>
    </div>
    
    <div class="filters">
        <strong>Target Roles:</strong>
        {" ".join([f'<span>{r}</span>' for r in profile.target_roles])}
    </div>
    
    <div class="job-list">
"""
    
    # Add job cards
    for rank, item in enumerate(jobs[:30], 1):
        # Handle both ScoringResult objects and dicts
        if hasattr(item, 'job'):
            job = item.job
            score = item.score
        else:
            job = item.get("job", {})
            score = item.get("score", {})
        
        # Extract values with fallback
        score_val = score.total_score if hasattr(score, 'total_score') else score.get("total_score", 0)
        label = score.score_label if hasattr(score, 'score_label') else score.get("score_label", "Moderate Match")
        
        # Job fields
        job_title = job.title if hasattr(job, 'title') else job.get('title', 'N/A')
        job_company = job.company if hasattr(job, 'company') else job.get('company', 'N/A')
        is_remote = job.is_remote if hasattr(job, 'is_remote') else job.get('is_remote', False)
        job_location = job.location if hasattr(job, 'location') else job.get('location', 'N/A')
        salary_display = job.salary_display if hasattr(job, 'salary_display') else job.get('salary_display', 'Not disclosed')
        posted_date = job.posted_date if hasattr(job, 'posted_date') else job.get('posted_date', 'N/A')
        apply_url = job.apply_url if hasattr(job, 'apply_url') else job.get('apply_url', '#')
        
        # Skills
        matched = score.matched_skills if hasattr(score, 'matched_skills') else score.get("matched_skills", [])
        if isinstance(matched, str):
            matched = matched.split(',') if matched else []
        
        missing = score.missing_skills if hasattr(score, 'missing_skills') else score.get("missing_skills", [])
        if isinstance(missing, str):
            missing = missing.split(',') if missing else []
        
        # Determine card class
        if score_val >= 75:
            card_class = "high"
        elif score_val >= 50:
            card_class = "medium"
        else:
            card_class = "low"
        
        # Determine badge class
        badge_class = label.lower().replace(" ", "-")
        
        html += f"""
        <div class="job-card {card_class}">
            <div class="job-header">
                <div>
                    <h3 class="job-title">{rank}. {job_title}</h3>
                    <div class="job-company">{job_company}</div>
                </div>
                <div class="score-badge {badge_class}">{score_val:.1f}%</div>
            </div>
            <div class="job-meta">
                <span>📍 {'Remote' if is_remote else job_location}</span>
                <span>💰 {salary_display}</span>
                <span>📅 {posted_date}</span>
            </div>
            <div class="skills">
"""
        
        # Add matched skills
        for skill in matched[:5]:
            html += f'<span class="skill-tag">{skill.strip()}</span>'
        
        # Add missing skills
        for skill in missing[:3]:
            html += f'<span class="skill-tag missing">{skill.strip()}</span>'
        
        html += f"""
            </div>
            <div class="job-actions">
                <a href="{apply_url}" class="btn" target="_blank">Apply Now →</a>
            </div>
        </div>
"""
    
    html += f"""
    </div>
    
    <div class="footer">
        <p>Generated by AI Job Intelligence Platform MVP</p>
        <p>For educational purposes only</p>
    </div>
</body>
</html>
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return output_path


def generate_markdown_report(
    jobs: List[Dict[str, Any]],
    profile: Profile,
    output_path: str = "data/job_report.md",
) -> str:
    """
    Generate a Markdown report.
    
    Args:
        jobs: List of job dictionaries with scores
        profile: User profile
        output_path: Path for output file
        
    Returns:
        Path to created report
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    lines = []
    
    # Header
    lines.append("# AI Job Intelligence - Job Match Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Profile:** {profile.name}")
    lines.append(f"**Target Roles:** {', '.join(profile.target_roles[:5])}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Jobs Found:** {len(jobs)}")
    
    if jobs:
        # Handle both ScoringResult objects and dicts
        scores = []
        for item in jobs:
            if hasattr(item, 'score'):
                scores.append(item.score.total_score)
            elif isinstance(item, dict) and "score" in item:
                scores.append(item["score"]["total_score"])
        
        if scores:
            lines.append(f"- **Average Match Score:** {sum(scores) / len(scores):.1f}%")
            lines.append(f"- **Highest Match:** {max(scores):.1f}%")
    
    lines.append("")
    lines.append("## Top Job Matches")
    lines.append("")
    
    # Jobs table
    lines.append("| Rank | Title | Company | Location | Score | Matched Skills |")
    lines.append("|------|-------|---------|----------|-------|-----------------|")
    
    for rank, item in enumerate(jobs[:20], 1):
        # Handle both ScoringResult objects and dicts
        if hasattr(item, 'job'):
            job = item.job
            score = item.score
        else:
            job = item.get("job", {})
            score = item.get("score", {})
        
        # Extract values
        job_title = job.title if hasattr(job, 'title') else job.get('title', 'N/A')
        job_company = job.company if hasattr(job, 'company') else job.get('company', 'N/A')
        is_remote = job.is_remote if hasattr(job, 'is_remote') else job.get('is_remote', False)
        job_location = job.location if hasattr(job, 'location') else job.get('location', 'N/A')
        
        score_val = score.total_score if hasattr(score, 'total_score') else score.get("total_score", 0)
        
        matched = score.matched_skills if hasattr(score, 'matched_skills') else score.get("matched_skills", [])
        if isinstance(matched, str):
            matched = matched.split(',') if matched else []
        
        location = "Remote" if is_remote else job_location
        skills = ", ".join(matched[:3]) if matched else ""
        
        lines.append(f"| {rank} | {job_title} | {job_company} | {location} | {score_val:.1f}% | {skills} |")
    
    lines.append("")
    lines.append("---")
    lines.append("*Generated by AI Job Intelligence Platform MVP*")
    
    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path