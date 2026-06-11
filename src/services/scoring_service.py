"""Scoring service for job-profile matching."""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.models.profile import Profile
from src.models.job import Job, JobSkill
from src.models.score import JobScore, Recommendation
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScoringWeights:
    """Weights for job scoring components."""
    skills: float = 0.40
    title: float = 0.30
    location: float = 0.15
    salary: float = 0.10
    experience: float = 0.05


class ScoringService:
    """Service for scoring jobs against profiles."""

    # Default weights
    DEFAULT_WEIGHTS = ScoringWeights()

    def __init__(self, db: Session):
        """Initialize scoring service with database session."""
        self.db = db

    def score_job(
        self,
        job_id: int,
        profile_id: int,
        weights: Optional[ScoringWeights] = None,
    ) -> JobScore:
        """
        Score a single job against a profile.
        
        Args:
            job_id: Job ID
            profile_id: Profile ID
            weights: Custom scoring weights
            
        Returns:
            JobScore: Calculated score
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        job = self.db.query(Job).filter(Job.id == job_id).first()
        profile = self.db.query(Profile).filter(Profile.id == profile_id).first()

        if not job or not profile:
            raise ValueError(f"Job {job_id} or Profile {profile_id} not found")

        # Calculate component scores
        skills_score = self._calculate_skills_score(job, profile)
        title_score = self._calculate_title_score(job, profile)
        location_score = self._calculate_location_score(job, profile)
        salary_score = self._calculate_salary_score(job, profile)
        experience_score = self._calculate_experience_score(job, profile)

        # Calculate weighted total
        total_score = (
            skills_score * weights.skills
            + title_score * weights.title
            + location_score * weights.location
            + salary_score * weights.salary
            + experience_score * weights.experience
        )

        # Get matched and missing skills
        job_skills = [s.skill_name for s in job.skills]
        profile_skills = self._get_profile_skills(profile)
        matched, missing = self._match_skills(job_skills, profile_skills)

        # Create or update score
        score = (
            self.db.query(JobScore)
            .filter(
                JobScore.job_id == job_id,
                JobScore.profile_id == profile_id,
            )
            .first()
        )

        if score:
            score.total_score = total_score
            score.skills_score = skills_score
            score.title_score = title_score
            score.location_score = location_score
            score.salary_score = salary_score
            score.experience_score = experience_score
            score.matched_skills = json.dumps(matched)
            score.missing_skills = json.dumps(missing)
        else:
            score = JobScore(
                profile_id=profile_id,
                job_id=job_id,
                total_score=total_score,
                skills_score=skills_score,
                title_score=title_score,
                location_score=location_score,
                salary_score=salary_score,
                experience_score=experience_score,
                matched_skills=json.dumps(matched),
                missing_skills=json.dumps(missing),
                scoring_method="weighted",
            )
            self.db.add(score)

        self.db.commit()
        self.db.refresh(score)

        logger.info(f"Scored job {job_id} for profile {profile_id}: {total_score:.1f}")
        return score

    def score_all_jobs(
        self,
        profile_id: int,
        min_score: float = 0,
        weights: Optional[ScoringWeights] = None,
    ) -> List[JobScore]:
        """
        Score all active jobs for a profile.
        
        Args:
            profile_id: Profile ID
            min_score: Minimum score threshold
            weights: Custom scoring weights
            
        Returns:
            List of JobScore instances
        """
        jobs = self.db.query(Job).filter(Job.is_active == True).all()
        scores = []

        for job in jobs:
            try:
                score = self.score_job(job.id, profile_id, weights)
                if score.total_score >= min_score:
                    scores.append(score)
            except Exception as e:
                logger.error(f"Error scoring job {job.id}: {e}")

        return scores

    def get_top_jobs(
        self,
        profile_id: int,
        limit: int = 20,
        min_score: float = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get top matching jobs for a profile.
        
        Args:
            profile_id: Profile ID
            limit: Maximum number of results
            min_score: Minimum score threshold
            
        Returns:
            List of job dictionaries with scores
        """
        scores = (
            self.db.query(JobScore)
            .filter(JobScore.profile_id == profile_id)
            .filter(JobScore.total_score >= min_score)
            .order_by(JobScore.total_score.desc())
            .limit(limit)
            .all()
        )

        results = []
        for score in scores:
            job = self.db.query(Job).filter(Job.id == score.job_id).first()
            if job:
                results.append({
                    "job": job.to_dict(),
                    "score": score.to_dict(),
                })

        return results

    # =============================================================================
    # Scoring Components
    # =============================================================================

    def _calculate_skills_score(self, job: Job, profile: Profile) -> float:
        """Calculate skills match score (0-100)."""
        job_skills = set(s.skill_name.lower() for s in job.skills)
        
        if not job_skills:
            return 50  # Neutral if no skills extracted
        
        profile_skills = set(s.lower() for s in self._get_profile_skills(profile))
        
        if not profile_skills:
            return 50  # Neutral if no profile skills
        
        # Calculate Jaccard similarity
        intersection = len(job_skills & profile_skills)
        union = len(job_skills | profile_skills)
        
        if union == 0:
            return 50
        
        similarity = intersection / union
        
        # Bonus for having most profile skills in job
        if profile_skills:
            coverage = len(job_skills & profile_skills) / len(profile_skills)
            score = (similarity * 0.5 + coverage * 0.5) * 100
        else:
            score = similarity * 100
        
        return min(100, max(0, score))

    def _calculate_title_score(self, job: Job, profile: Profile) -> float:
        """Calculate title match score (0-100)."""
        target_roles = profile.target_roles_list
        
        if not target_roles:
            return 50  # Neutral
        
        job_title_lower = job.title.lower()
        
        # Check for exact or partial matches
        matches = 0
        for role in target_roles:
            role_lower = role.lower()
            if role_lower in job_title_lower:
                matches += 1
            # Check for partial word matches
            role_words = role_lower.split()
            for word in role_words:
                if len(word) > 3 and word in job_title_lower:
                    matches += 0.5
        
        # Normalize score
        if matches >= len(target_roles):
            return 100
        elif matches > 0:
            return 50 + (matches / len(target_roles)) * 50
        else:
            return 25  # Low score if no match

    def _calculate_location_score(self, job: Job, profile: Profile) -> float:
        """Calculate location match score (0-100)."""
        preferred_locations = profile.locations_list
        
        if not preferred_locations:
            return 50  # Neutral
        
        job_location = (job.location or "").lower()
        is_remote = job.is_remote
        
        # Check for remote match
        if is_remote and "remote" in [loc.lower() for loc in preferred_locations]:
            return 100
        
        # Check for location matches
        for loc in preferred_locations:
            loc_lower = loc.lower()
            if loc_lower == "remote" and is_remote:
                return 100
            if loc_lower in job_location or job_location in loc_lower:
                return 100
        
        # Partial location match
        if job_location:
            return 50
        
        return 25  # No location info

    def _calculate_salary_score(self, job: Job, profile: Profile) -> float:
        """Calculate salary match score (0-100)."""
        if not job.salary_min and not job.salary_max:
            return 50  # Neutral if no salary info
        
        profile_min = profile.salary_min or 0
        profile_max = profile.salary_max or float("inf")
        
        job_min = job.salary_min or 0
        job_max = job.salary_max or float("inf")
        
        # Check for overlap
        if job_max < profile_min:
            # Job pays too little
            return max(0, 100 - (profile_min - job_max) / profile_min * 100)
        elif job_min > profile_max:
            # Job pays too much (unlikely to get)
            return 75  # Still possible
        else:
            # Ranges overlap - good match
            return 100

    def _calculate_experience_score(self, job: Job, profile: Profile) -> float:
        """Calculate experience match score (0-100)."""
        profile_exp = profile.experience_years or 0
        
        if not job.requirements:
            return 50  # Neutral
        
        # Try to extract required years from requirements
        import re
        exp_match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)", job.requirements.lower())
        
        if exp_match:
            required_exp = int(exp_match.group(1))
            
            if profile_exp >= required_exp:
                return 100
            elif profile_exp >= required_exp - 2:
                return 75  # Close
            else:
                return max(0, 50 - (required_exp - profile_exp) * 10)
        
        return 50  # Neutral if can't determine

    # =============================================================================
    # Helper Methods
    # =============================================================================

    def _get_profile_skills(self, profile: Profile) -> List[str]:
        """Get profile skills from association table."""
        from src.models.profile import profile_skills
        
        # Query the association table
        skills = (
            self.db.execute(
                profile_skills.select()
                .where(profile_skills.c.profile_id == profile.id)
            )
            .fetchall()
        )
        
        return [s.skill_name for s in skills]

    def _match_skills(
        self,
        job_skills: List[str],
        profile_skills: List[str],
    ) -> tuple[List[str], List[str]]:
        """Match job skills to profile skills."""
        job_skills_set = set(s.lower() for s in job_skills)
        profile_skills_set = set(s.lower() for s in profile_skills)
        
        matched = list(job_skills_set & profile_skills_set)
        missing = list(profile_skills_set - job_skills_set)
        
        return matched, missing

    # =============================================================================
    # Recommendations
    # =============================================================================

    def generate_recommendations(
        self,
        profile_id: int,
        limit: int = 10,
    ) -> List[Recommendation]:
        """
        Generate recommendations for a profile.
        
        Args:
            profile_id: Profile ID
            limit: Maximum number of recommendations
            
        Returns:
            List of Recommendation instances
        """
        top_jobs = self.get_top_jobs(profile_id, limit=limit * 2, min_score=60)
        
        recommendations = []
        
        for item in top_jobs[:limit]:
            job_dict = item["job"]
            score_dict = item["score"]
            
            # Determine recommendation type
            if score_dict["total_score"] >= 80:
                rec_type = "apply"
                priority = 1
            elif score_dict["total_score"] >= 60:
                rec_type = "research"
                priority = 2
            else:
                rec_type = "watch"
                priority = 3
            
            # Generate reason
            matched = score_dict.get("matched_skills", [])
            missing = score_dict.get("missing_skills", [])
            
            if matched:
                reason = f"Matches your skills: {', '.join(matched[:3])}"
            else:
                reason = "Good match for your target roles"
            
            if missing:
                reason += f". Consider developing: {', '.join(missing[:2])}"
            
            # Create recommendation
            rec = Recommendation(
                profile_id=profile_id,
                job_id=job_dict["id"],
                recommendation_type=rec_type,
                priority=priority,
                reason=reason,
                action_items=json.dumps([
                    f"Review job description",
                    f"Update resume for {job_dict['title']}",
                    "Prepare for technical questions",
                ]),
            )
            
            self.db.add(rec)
            recommendations.append(rec)
        
        self.db.commit()
        
        logger.info(f"Generated {len(recommendations)} recommendations for profile {profile_id}")
        return recommendations