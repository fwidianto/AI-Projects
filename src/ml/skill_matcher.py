"""Skill matcher using embeddings."""

from typing import List, Dict, Optional
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SkillMatcher:
    """Skill matching using semantic embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize skill matcher with embedding model."""
        self.model_name = model_name
        self._model = None
        self._initialized = False

    def initialize(self):
        """Initialize the embedding model."""
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._initialized = True
            logger.info("Embedding model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback matching.")
            self._initialized = True  # Mark as initialized to prevent retry

    @property
    def model(self):
        """Lazy load model."""
        if not self._initialized:
            self.initialize()
        return self._model

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings."""
        if self.model is None:
            # Fallback to simple token matching
            return np.zeros((len(texts), 1))

        return self.model.encode(texts, show_progress_bar=False)

    def calculate_similarity(
        self,
        profile_skills: List[str],
        job_skills: List[str],
    ) -> float:
        """
        Calculate semantic similarity between profile and job skills.
        
        Args:
            profile_skills: List of profile skills
            job_skills: List of job skills
            
        Returns:
            float: Similarity score (0.0 - 1.0)
        """
        if not profile_skills or not job_skills:
            return 0.0

        if self.model is None:
            return self._fallback_similarity(profile_skills, job_skills)

        # Encode skills
        all_skills = profile_skills + job_skills
        embeddings = self.encode(all_skills)

        profile_embeddings = embeddings[: len(profile_skills)]
        job_embeddings = embeddings[len(profile_skills) :]

        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(profile_embeddings, job_embeddings)

        # Get max similarity for each profile skill
        max_similarities = np.max(similarity_matrix, axis=1)

        # Return average similarity
        return float(np.mean(max_similarities))

    def _fallback_similarity(
        self,
        profile_skills: List[str],
        job_skills: List[str],
    ) -> float:
        """Fallback similarity using simple token matching."""
        profile_lower = [s.lower() for s in profile_skills]
        job_lower = [s.lower() for s in job_skills]

        matches = sum(1 for ps in profile_lower for js in job_lower if ps in js or js in ps)
        total = len(profile_skills) + len(job_skills)

        return matches / total if total > 0 else 0.0

    def find_similar_skills(
        self,
        skill: str,
        skill_pool: List[str],
        top_k: int = 5,
    ) -> List[Dict[str, any]]:
        """
        Find similar skills from a pool.
        
        Args:
            skill: Target skill
            skill_pool: Pool of skills to search
            top_k: Number of results to return
            
        Returns:
            List of similar skills with scores
        """
        if self.model is None:
            return []

        embeddings = self.encode([skill] + skill_pool)
        target_embedding = embeddings[0]
        pool_embeddings = embeddings[1:]

        from sklearn.metrics.pairwise import cosine_similarity

        similarities = cosine_similarity([target_embedding], pool_embeddings)[0]

        results = []
        for i, sim in enumerate(similarities):
            results.append({"skill": skill_pool[i], "score": float(sim)})

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]


# Global instance
_skill_matcher: Optional[SkillMatcher] = None


def get_skill_matcher() -> SkillMatcher:
    """Get or create global skill matcher instance."""
    global _skill_matcher
    if _skill_matcher is None:
        _skill_matcher = SkillMatcher()
    return _skill_matcher