"""Job classifier using zero-shot classification."""

from typing import List, Dict, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class JobClassifier:
    """Job classification using zero-shot learning."""

    JOB_CATEGORIES = [
        "erp_analyst",
        "business_analyst",
        "data_analyst",
        "operations_analyst",
        "finance_analyst",
        "software_engineer",
        "project_manager",
        "other",
    ]

    CATEGORY_DESCRIPTIONS = {
        "erp_analyst": "Jobs involving ERP systems like SAP, Odoo, Oracle, implementing, configuring, or supporting ERP software",
        "business_analyst": "Jobs involving business analysis, requirements gathering, stakeholder management, and process improvement",
        "data_analyst": "Jobs involving data analysis, SQL, reporting, BI tools, and analytics",
        "operations_analyst": "Jobs involving operations management, process improvement, supply chain, and logistics",
        "finance_analyst": "Jobs involving financial analysis, budgeting, cost control, and accounting",
        "software_engineer": "Jobs involving software development, programming, and technical implementation",
        "project_manager": "Jobs involving project management, planning, and coordination",
    }

    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """Initialize job classifier."""
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._initialized = False

    def initialize(self):
        """Load the classification model."""
        if self._initialized:
            return

        try:
            from transformers import pipeline

            logger.info(f"Loading classifier model: {self.model_name}")
            self._classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=-1,  # Use CPU
            )
            self._initialized = True
            logger.info("Classifier model loaded successfully")
        except ImportError:
            logger.warning("transformers not installed. Using rule-based classification.")
            self._initialized = True

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._classifier is not None

    def classify(
        self,
        job_title: str,
        job_description: str = "",
        top_k: int = 1,
    ) -> List[Dict[str, any]]:
        """
        Classify a job into categories.
        
        Args:
            job_title: Job title
            job_description: Job description (optional)
            top_k: Number of top categories to return
            
        Returns:
            List of category predictions with scores
        """
        if not self._initialized:
            self.initialize()

        # Combine title and description
        text = job_title
        if job_description:
            text = f"{job_title}. {job_description[:500]}"

        if self._classifier is not None:
            return self._classify_with_model(text, top_k)
        else:
            return self._classify_with_rules(text, top_k)

    def _classify_with_model(
        self,
        text: str,
        top_k: int,
    ) -> List[Dict[str, any]]:
        """Classify using ML model."""
        try:
            candidate_labels = [
                self.CATEGORY_DESCRIPTIONS[cat] for cat in self.JOB_CATEGORIES
            ]

            result = self._classifier(
                text,
                candidate_labels,
                multi_label=False,
            )

            predictions = []
            for label, score in zip(result["labels"], result["scores"]):
                # Map back to category
                category = self._get_category_from_description(label)
                predictions.append({
                    "category": category,
                    "score": float(score),
                })

            return predictions[:top_k]

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return self._classify_with_rules(text, top_k)

    def _classify_with_rules(
        self,
        text: str,
        top_k: int,
    ) -> List[Dict[str, any]]:
        """Fallback rule-based classification."""
        text_lower = text.lower()
        scores = {}

        # Define keyword mappings
        keywords = {
            "erp_analyst": [
                "erp", "sap", "odoo", "oracle", "functional consultant",
                "erp analyst", "erp consultant", "sap consultant",
            ],
            "business_analyst": [
                "business analyst", "ba", "requirements", "stakeholder",
                "functional analyst", "business process",
            ],
            "data_analyst": [
                "data analyst", "sql", "reporting", "bi", "analytics",
                "tableau", "power bi", "excel",
            ],
            "operations_analyst": [
                "operations", "process improvement", "supply chain",
                "logistics", "procurement", "inventory",
            ],
            "finance_analyst": [
                "finance", "financial", "budget", "cost control",
                "accounting", "cost analyst", "tax",
            ],
            "software_engineer": [
                "software", "developer", "programmer", "engineer",
                "python", "java", "javascript", "coding",
            ],
            "project_manager": [
                "project manager", "pm", "project lead", "scrum",
                "agile", "project coordinator",
            ],
        }

        # Calculate scores
        for category, cats_keywords in keywords.items():
            score = sum(1 for kw in cats_keywords if kw in text_lower)
            if score > 0:
                scores[category] = score

        # Sort by score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Normalize scores
        max_score = max(scores.values()) if scores else 1

        results = []
        for category, score in sorted_categories[:top_k]:
            results.append({
                "category": category,
                "score": score / max_score,
            })

        # If no matches, return "other"
        if not results:
            results = [{"category": "other", "score": 1.0}]

        return results

    def _get_category_from_description(self, description: str) -> str:
        """Map description back to category."""
        for category, desc in self.CATEGORY_DESCRIPTIONS.items():
            if description.lower() in desc.lower() or desc.lower() in description.lower():
                return category
        return "other"

    def get_category_label(self, category: str) -> str:
        """Get human-readable category label."""
        labels = {
            "erp_analyst": "ERP Analyst",
            "business_analyst": "Business Analyst",
            "data_analyst": "Data Analyst",
            "operations_analyst": "Operations Analyst",
            "finance_analyst": "Finance Analyst",
            "software_engineer": "Software Engineer",
            "project_manager": "Project Manager",
            "other": "Other",
        }
        return labels.get(category, "Other")


# Global instance
_classifier: Optional[JobClassifier] = None


def get_job_classifier() -> JobClassifier:
    """Get or create global job classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = JobClassifier()
    return _classifier