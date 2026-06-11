"""Embeddings model for text encoding."""

from typing import List, Optional
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingsModel:
    """Text embeddings model wrapper."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embeddings model."""
        self.model_name = model_name
        self._model = None
        self._initialized = False

    def initialize(self):
        """Load the embedding model."""
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embeddings model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._initialized = True
            logger.info("Embeddings model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed")
            self._initialized = True

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode texts to embeddings.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            numpy array of embeddings
        """
        if not self._initialized:
            self.initialize()

        if self._model is None:
            # Return zeros if model not available
            return np.zeros((len(texts), 384))

        return self._model.encode(texts, batch_size=batch_size, show_progress_bar=False)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text."""
        return self.encode([text])[0]

    def calculate_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Cosine similarity (0.0 - 1.0)
        """
        embeddings = self.encode([text1, text2])

        # Calculate cosine similarity
        dot_product = np.dot(embeddings[0], embeddings[1])
        norm1 = np.linalg.norm(embeddings[0])
        norm2 = np.linalg.norm(embeddings[1])

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
    ) -> List[tuple[str, float]]:
        """
        Find most similar texts to a query.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of results to return
            
        Returns:
            List of (text, similarity_score) tuples
        """
        if not candidates:
            return []

        all_texts = [query] + candidates
        embeddings = self.encode(all_texts)

        query_embedding = embeddings[0]
        candidate_embeddings = embeddings[1:]

        # Calculate similarities
        from sklearn.metrics.pairwise import cosine_similarity

        similarities = cosine_similarity([query_embedding], candidate_embeddings)[0]

        # Sort by similarity
        indexed_similarities = list(enumerate(similarities))
        indexed_similarities.sort(key=lambda x: x[1], reverse=True)

        results = [(candidates[i], float(score)) for i, score in indexed_similarities[:top_k]]

        return results


# Global instance
_embeddings: Optional[EmbeddingsModel] = None


def get_embeddings_model() -> EmbeddingsModel:
    """Get or create global embeddings model instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = EmbeddingsModel()
    return _embeddings