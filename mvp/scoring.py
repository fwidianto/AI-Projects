"""
MVP Job Scoring Module

Implements rule-based job scoring against user profile.

Assumptions:
    - Rule-based scoring is deterministic and explainable
    - Skills matching uses keyword extraction (no ML embeddings for MVP)
    - All scores are normalized to 0-100 scale
    - Weights can be customized per user
"""

import re
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from difflib import SequenceMatcher

from mvp.database import Job, JobScore
from mvp.config_loader import Profile, ScoringWeights, Skill


@dataclass
class ScoringResult:
    """Result of scoring a job."""
    job: Job
    score: JobScore
    analysis: str


class JobScorer:
    """
    Rule-based job scorer.
    
    Scoring Components:
        1. Skills Match (40%): Match job requirements to profile skills
        2. Title Match (30%): Match job title to target roles
        3. Location Match (15%): Check if location matches preferences
        4. Salary Match (10%): Check if salary range overlaps
        5. Experience Match (5%): Check experience requirements
    
    Assumptions:
        - Keyword matching is sufficient for MVP
        - Exact skill matches are worth more than partial matches
        - Location matching is binary (match/no match)
        - Salary overlap calculation is straightforward
    """
    
    # Common skill variations and synonyms
    SKILL_ALIASES = {
        "sap": ["SAP", "SAP ECC", "SAP ERP", "SAP S/4HANA", "SAP FI", "SAP CO", "SAP MM", "SAP SD"],
        "odoo": ["Odoo", "Odoo ERP", "OpenERP"],
        "sql": ["SQL", "MySQL", "PostgreSQL", "Database"],
        "excel": ["Excel", "Microsoft Excel", "Spreadsheet"],
        "bi": ["BI", "Business Intelligence", "Power BI", "Tableau", "Looker", "Looker Studio"],
        "python": ["Python", "Python Programming"],
        "process": ["Process", "Process Improvement", "Process Optimization"],
        "cost": ["Cost", "Cost Control", "Cost Management"],
        "budget": ["Budget", "Budgeting", "Budget Management"],
        "data": ["Data", "Data Analysis", "Data Analytics"],
        "reporting": ["Report", "Reporting", "Report Writing"],
        "erp": ["ERP", "ERP System", "ERP Analyst", "ERP Consultant"],
        "analysis": ["Analysis", "Analyst", "Analytics"],
        "finance": ["Finance", "Financial", "Financial Analysis"],
        "operations": ["Operations", "Operations Analyst", "Ops"],
    }
    
    def __init__(self, profile: Profile, weights: ScoringWeights):
        """
        Initialize scorer with user profile.
        
        Args:
            profile: User profile configuration
            weights: Scoring weight configuration
        """
        self.profile = profile
        self.weights = weights
        
        # Build normalized skill lookup
        self._build_skill_lookup()
    
    def _build_skill_lookup(self) -> None:
        """Build skill lookup dictionary for matching."""
        self.skill_lookup: Dict[str, Set[str]] = {}
        
        # Add profile skills
        for skill in self.profile.skills:
            skill_lower = skill.name.lower()
            self.skill_lookup[skill_lower] = {skill.name}
            
            # Add aliases
            for alias_key, aliases in self.SKILL_ALIASES.items():
                if alias_key in skill_lower or skill_lower in alias_key:
                    self.skill_lookup[skill_lower].update(aliases)
    
    def score_job(self, job: Job) -> Tuple[JobScore, str]:
        """
        Score a single job against the profile.
        
        Args:
            job: Job to score
            
        Returns:
            Tuple of (JobScore, analysis_string)
            
        Assumptions:
            - Description text is the primary source for skill matching
            - Title contains important keywords
            - Requirements section has high priority for skill extraction
        """
        # Combine text for analysis
        full_text = f"{job.title} {job.description} {job.requirements}".lower()
        
        # Calculate component scores
        skills_score, matched, missing = self._score_skills(full_text)
        title_score = self._score_title(job.title)
        location_score = self._score_location(job.location, job.is_remote)
        salary_score = self._score_salary(job.salary_min, job.salary_max)
        experience_score = self._score_experience(full_text)
        
        # Calculate weighted total
        total_score = (
            skills_score * self.weights.skills_match +
            title_score * self.weights.title_match +
            location_score * self.weights.location_match +
            salary_score * self.weights.salary_match +
            experience_score * self.weights.experience_match
        )
        
        # Create score object
        score = JobScore(
            job_id=job.id or 0,
            total_score=total_score,
            skills_score=skills_score,
            title_score=title_score,
            location_score=location_score,
            salary_score=salary_score,
            experience_score=experience_score,
            matched_skills=",".join(matched),
            missing_skills=",".join(missing),
        )
        
        # Generate analysis
        analysis = self._generate_analysis(
            job, skills_score, title_score, location_score, 
            salary_score, experience_score, matched, missing
        )
        
        return score, analysis
    
    def _score_skills(self, text: str) -> Tuple[float, List[str], List[str]]:
        """
        Score skills match between profile and job.
        
        Args:
            text: Combined job text
            
        Returns:
            Tuple of (score, matched_skills, missing_skills)
        """
        found_skills: Set[str] = set()
        
        # Check each profile skill
        for skill in self.profile.skills:
            skill_lower = skill.name.lower()
            
            # Direct match
            if skill_lower in text:
                found_skills.add(skill.name)
                continue
            
            # Check aliases
            if skill_lower in self.skill_lookup:
                for alias in self.skill_lookup[skill_lower]:
                    if alias.lower() in text:
                        found_skills.add(skill.name)
                        break
            
            # Fuzzy match for compound skills
            skill_words = skill_lower.split()
            if len(skill_words) >= 2:
                if all(word in text for word in skill_words):
                    found_skills.add(skill.name)
        
        # Calculate score based on coverage
        total_skills = len(self.profile.skills)
        key_skills = [s for s in self.profile.skills if s.is_key_skill]
        key_skill_names = [s.name for s in key_skills]
        
        if total_skills == 0:
            return 50.0, [], []
        
        # Weight key skills more heavily
        matched_key = len([s for s in found_skills if s in key_skill_names])
        key_skill_count = len(key_skills) if key_skills else 1
        
        # Score calculation
        base_score = (len(found_skills) / total_skills) * 100
        key_bonus = (matched_key / key_skill_count) * 20 if key_skills else 0
        
        score = min(100, base_score + key_bonus)
        
        matched = list(found_skills)
        missing = [s.name for s in self.profile.skills if s.name not in found_skills]
        
        return score, matched, missing
    
    def _score_title(self, title: str) -> float:
        """
        Score title match against target roles.
        
        Args:
            title: Job title
            
        Returns:
            Score from 0-100
        """
        if not self.profile.target_roles or not title:
            return 50.0
        
        title_lower = title.lower()
        best_match = 0.0
        
        for role in self.profile.target_roles:
            role_lower = role.lower()
            
            # Exact match
            if role_lower == title_lower:
                return 100.0
            
            # Title contains role
            if role_lower in title_lower:
                return 90.0
            
            # Partial word match
            role_words = role_lower.split()
            matches = sum(1 for word in role_words if word in title_lower and len(word) > 3)
            if matches:
                match_ratio = matches / len(role_words)
                best_match = max(best_match, match_ratio * 80)
            
            # Fuzzy matching for similar words
            similarity = SequenceMatcher(None, role_lower, title_lower).ratio()
            if similarity > 0.6:
                best_match = max(best_match, similarity * 100)
        
        return best_match if best_match > 0 else 25.0
    
    def _score_location(self, location: str, is_remote: bool) -> float:
        """
        Score location match against preferences.
        
        Args:
            location: Job location
            is_remote: Whether job is remote
            
        Returns:
            Score from 0-100
        """
        if not self.profile.preferred_locations:
            return 50.0
        
        if is_remote and "remote" in [l.lower() for l in self.profile.preferred_locations]:
            return 100.0
        
        if not location:
            return 40.0
        
        location_lower = location.lower()
        
        for pref in self.profile.preferred_locations:
            pref_lower = pref.lower()
            
            if pref_lower == "remote":
                continue
            
            if pref_lower in location_lower or location_lower in pref_lower:
                return 100.0
            
            # Jakarta variations
            jakarta_variations = ["jakarta", "jk", "dki"]
            if any(var in location_lower for var in jakarta_variations):
                if "jakarta" in pref_lower:
                    return 100.0
        
        return 30.0  # No match
    
    def _score_salary(self, salary_min: int, salary_max: int) -> float:
        """
        Score salary match against expectations.
        
        Args:
            salary_min: Minimum salary from job
            salary_max: Maximum salary from job
            
        Returns:
            Score from 0-100
        """
        exp_min = self.profile.salary_expectations.min
        exp_max = self.profile.salary_expectations.max
        
        # No salary info
        if not salary_min and not salary_max:
            return 50.0
        
        # Use available values
        job_min = salary_min or salary_max or 0
        job_max = salary_max or salary_min or job_min
        
        # Calculate overlap
        if job_max < exp_min:
            # Job pays below minimum expectation
            gap = exp_min - job_max
            return max(0, 50 - (gap / exp_min * 100))
        
        if job_min > exp_max:
            # Job pays above (can still apply)
            return 75.0
        
        # Good overlap
        overlap_min = max(job_min, exp_min)
        overlap_max = min(job_max, exp_max)
        overlap = overlap_max - overlap_min
        
        # Calculate how much of expectation range is covered
        exp_range = exp_max - exp_min
        if exp_range > 0:
            coverage = overlap / exp_range
            return 70 + (coverage * 30)  # 70-100 range
        
        return 85.0  # Default good match
    
    def _score_experience(self, text: str) -> float:
        """
        Score experience requirements match.
        
        Args:
            text: Combined job text
            
        Returns:
            Score from 0-100
        """
        profile_exp = self.profile.experience_years
        
        # Extract required years
        years_patterns = [
            r"(\d+)\+?\s*(?:years?|yrs?)",
            r"minimum\s*(?:of\s*)?(\d+)",
            r"at\s*least\s*(\d+)",
        ]
        
        required_years = 0
        for pattern in years_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                years = [int(m) for m in matches]
                required_years = max(required_years, max(years))
        
        if required_years == 0:
            return 50.0  # No specific requirement
        
        if profile_exp >= required_years:
            # Good match
            if profile_exp >= required_years + 3:
                return 75.0  # Overqualified but okay
            return 100.0
        
        # Underqualified
        gap = required_years - profile_exp
        if gap <= 2:
            return 60.0  # Close
        return max(0, 40 - gap * 10)
    
    def _generate_analysis(
        self,
        job: Job,
        skills_score: float,
        title_score: float,
        location_score: float,
        salary_score: float,
        experience_score: float,
        matched: List[str],
        missing: List[str],
    ) -> str:
        """Generate human-readable analysis."""
        lines = [
            f"Job: {job.title} at {job.company}",
            f"Overall Match: {skills_score * self.weights.skills_match + title_score * self.weights.title_match + location_score * self.weights.location_match + salary_score * self.weights.salary_match + experience_score * self.weights.experience_match:.1f}%",
            "",
            "Component Scores:",
            f"  Skills Match: {skills_score:.1f}% (weight: {self.weights.skills_match * 100:.0f}%)",
            f"  Title Match: {title_score:.1f}% (weight: {self.weights.title_match * 100:.0f}%)",
            f"  Location Match: {location_score:.1f}% (weight: {self.weights.location_match * 100:.0f}%)",
            f"  Salary Match: {salary_score:.1f}% (weight: {self.weights.salary_match * 100:.0f}%)",
            f"  Experience Match: {experience_score:.1f}% (weight: {self.weights.experience_match * 100:.0f}%)",
        ]
        
        if matched:
            lines.append("")
            lines.append(f"Matched Skills ({len(matched)}): {', '.join(matched[:5])}")
        
        if missing:
            lines.append(f"Missing Skills: {', '.join(missing[:5])}")
        
        return "\n".join(lines)
    
    def score_jobs(self, jobs: List[Job]) -> List[ScoringResult]:
        """
        Score multiple jobs.
        
        Args:
            jobs: List of jobs to score
            
        Returns:
            List of ScoringResult objects sorted by score descending
        """
        results = []
        
        for job in jobs:
            if job.id is None:
                continue
                
            score, analysis = self.score_job(job)
            score.job_id = job.id
            results.append(ScoringResult(job=job, score=score, analysis=analysis))
        
        # Sort by total score descending
        results.sort(key=lambda x: x.score.total_score, reverse=True)
        
        return results