"""NLP service for text processing and skill extraction."""

from typing import List, Dict, Optional, Tuple
import re

from src.utils.logger import get_logger

logger = get_logger(__name__)


class NLPService:
    """Service for NLP operations like skill extraction and text processing."""

    # Skills taxonomy
    SKILLS_TAXONOMY = {
        "technical": [
            # ERP Systems
            "SAP ECC", "SAP S/4HANA", "SAP FI", "SAP CO", "SAP MM", "SAP SD", "SAP ABAP",
            "Odoo", "Odoo ERP", "SAP Business One",
            # Databases & BI
            "SQL", "MySQL", "PostgreSQL", "MongoDB",
            "Power BI", "Tableau", "Looker", "Looker Studio",
            "SAP BusinessObjects", "Crystal Reports",
            # Programming
            "Python", "Java", "JavaScript", "R", "VBA", "Excel VBA",
            "REST API", "API Integration",
            # Data Tools
            "ETL", "Data Modeling", "Data Warehouse",
            "pandas", "numpy", "scikit-learn",
            "Google Sheets", "Microsoft Excel",
            # Cloud
            "AWS", "Azure", "Google Cloud", "GCP",
        ],
        "business": [
            # Business Analysis
            "Business Analysis", "Requirements Gathering", "Process Analysis",
            "Stakeholder Management", "Business Requirements",
            "Gap Analysis", "Use Case Analysis",
            # Finance
            "Cost Control", "Budgeting", "Financial Analysis",
            "Cost Accounting", "Financial Reporting",
            "Budget Planning", "Cost Analysis",
            # Operations
            "Process Improvement", "Lean", "Six Sigma",
            "Operations Management", "Supply Chain",
            "Inventory Management", "Procurement",
            # ERP Domain
            "ERP Implementation", "ERP Support", "ERP Configuration",
            "Business Process", "Workflow Design",
            "Master Data", "Data Migration",
        ],
        "soft": [
            "Communication", "Presentation", "Report Writing",
            "Problem Solving", "Analytical Thinking",
            "Team Collaboration", "Project Management",
            "Time Management", "Attention to Detail",
        ],
    }

    # Flatten skills for matching
    ALL_SKILLS = [s for skills in SKILLS_TAXONOMY.values() for s in skills]

    def __init__(self):
        """Initialize NLP service."""
        self._skill_patterns = self._compile_skill_patterns()

    def _compile_skill_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for skill matching."""
        patterns = {}
        for skill in self.ALL_SKILLS:
            # Escape special characters and create word boundary pattern
            escaped = re.escape(skill)
            patterns[skill] = re.compile(
                r"\b" + escaped + r"\b",
                re.IGNORECASE,
            )
        return patterns

    def extract_skills(self, text: str) -> List[Dict[str, any]]:
        """
        Extract skills from text.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of skill dictionaries with name and confidence
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        for skill, pattern in self._skill_patterns.items():
            if pattern.search(text):
                # Determine confidence based on context
                confidence = self._calculate_skill_confidence(text, skill)
                found_skills.append({
                    "name": skill,
                    "confidence": confidence,
                    "category": self._get_skill_category(skill),
                })
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill["name"] not in seen:
                seen.add(skill["name"])
                unique_skills.append(skill)
        
        unique_skills.sort(key=lambda x: x["confidence"], reverse=True)
        
        logger.info(f"Extracted {len(unique_skills)} skills from text")
        return unique_skills

    def _calculate_skill_confidence(self, text: str, skill: str) -> float:
        """
        Calculate confidence score for a skill match.
        
        Args:
            text: Source text
            skill: Skill name
            
        Returns:
            float: Confidence score (0.0 - 1.0)
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Count occurrences
        count = text_lower.count(skill_lower)
        
        # Base confidence
        confidence = 0.7
        
        # Boost for multiple mentions
        if count > 1:
            confidence += min(0.2, (count - 1) * 0.1)
        
        # Boost for skill in title/header position
        first_500 = text_lower[:500]
        if skill_lower in first_500:
            confidence += 0.1
        
        # Boost for skill in requirements section
        if "requirement" in text_lower or "qualification" in text_lower:
            if skill_lower in text_lower:
                confidence += 0.05
        
        return min(1.0, confidence)

    def _get_skill_category(self, skill: str) -> str:
        """Get category for a skill."""
        for category, skills in self.SKILLS_TAXONOMY.items():
            if skill in skills:
                return category
        return "other"

    def clean_html(self, html: str) -> str:
        """
        Clean HTML content to plain text.
        
        Args:
            html: HTML content
            
        Returns:
            str: Cleaned plain text
        """
        import html2text
        
        if not html:
            return ""
        
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True
        
        text = h.handle(html)
        
        # Clean up whitespace
        text = " ".join(text.split())
        
        return text.strip()

    def extract_job_requirements(self, text: str) -> List[str]:
        """
        Extract requirements from job description.
        
        Args:
            text: Job description text
            
        Returns:
            List of requirement strings
        """
        if not text:
            return []
        
        requirements = []
        
        # Look for requirements section
        req_patterns = [
            r"requirements?[:\s]*(.*?)(?=qualifications?|benefits?|responsibilities?|$)",
            r"qualifications?[:\s]*(.*?)(?=requirements?|benefits?|responsibilities?|$)",
            r"what you[' ]?ll do[:\s]*(.*?)(?=requirements?|qualifications?|benefits?|$)",
        ]
        
        for pattern in req_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1)
                # Split by common delimiters
                items = re.split(r"[•\-\*•·\n]", section)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 10:
                        requirements.append(item)
        
        # If no structured requirements found, extract bullet points
        if not requirements:
            bullet_pattern = r"^[•\-\*·]\s*(.+)$"
            matches = re.findall(bullet_pattern, text, re.MULTILINE)
            requirements = [m.strip() for m in matches if len(m.strip()) > 10]
        
        return requirements[:20]  # Limit to 20 requirements

    def extract_benefits(self, text: str) -> List[str]:
        """
        Extract benefits from job description.
        
        Args:
            text: Job description text
            
        Returns:
            List of benefit strings
        """
        if not text:
            return []
        
        benefits = []
        
        # Look for benefits section
        benefit_patterns = [
            r"benefits?[:\s]*(.*?)(?=about|how to apply|application|$)",
            r"what we offer[:\s]*(.*?)(?=about|how to apply|application|$)",
        ]
        
        for pattern in benefit_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1)
                items = re.split(r"[•\-\*·\n]", section)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 5:
                        benefits.append(item)
        
        return benefits[:15]

    def classify_job_type(self, title: str, description: str = "") -> str:
        """
        Classify job into standard categories.
        
        Args:
            title: Job title
            description: Job description
            
        Returns:
            str: Job type classification
        """
        text = (title + " " + description).lower()
        
        classifications = {
            "erp_analyst": [
                "erp analyst", "sap analyst", "sap consultant", "odoo",
                "erp consultant", "erp support", "functional consultant",
            ],
            "business_analyst": [
                "business analyst", "ba", "requirements analyst",
                "functional analyst", "business system analyst",
            ],
            "data_analyst": [
                "data analyst", "analytics", "bi analyst", "reporting analyst",
                "sql analyst", "data engineer",
            ],
            "operations_analyst": [
                "operations analyst", "process analyst", "operations manager",
                "process improvement", "supply chain",
            ],
            "finance_analyst": [
                "finance analyst", "financial analyst", "cost analyst",
                "budget analyst", "accounting", "cost control",
            ],
        }
        
        for job_type, keywords in classifications.items():
            for keyword in keywords:
                if keyword in text:
                    return job_type
        
        return "other"

    def summarize_text(
        self,
        text: str,
        max_length: int = 200,
    ) -> str:
        """
        Summarize text to a maximum length.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            str: Summarized text
        """
        if not text:
            return ""
        
        # Simple extraction-based summarization
        # Split into sentences
        sentences = re.split(r"[.!?]+", text)
        
        summary = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if current_length + len(sentence) + 1 <= max_length:
                summary.append(sentence)
                current_length += len(sentence) + 1
            else:
                # Try to fit a partial sentence
                remaining = max_length - current_length - 4
                if remaining > 20:
                    summary.append(sentence[:remaining] + "...")
                break
        
        return ". ".join(summary)

    def extract_salary_info(self, text: str) -> Tuple[Optional[int], Optional[int], str]:
        """
        Extract salary information from text.
        
        Args:
            text: Text containing salary information
            
        Returns:
            Tuple of (min_salary, max_salary, currency)
        """
        if not text:
            return None, None, "IDR"
        
        # Indonesian salary patterns
        patterns = [
            # "Rp 15.000.000 - 25.000.000"
            r"rp\.?\s*(\d[\d.,]*)\s*[-–—to]+\s*(\d[\d.,]*)?",
            # "IDR 15jt - 25jt"
            r"idr\s*(\d+)\s*(?:jt|m)\s*[-–—to]+\s*(\d+)?\s*(?:jt|m)?",
            # "15-25 juta"
            r"(\d+)\s*[-–—to]+\s*(\d+)?\s*(?:juta|jt|m)",
            # "Salary: 15000000"
            r"salary[:\s]*(\d+)",
            # "Monthly: Rp15000000"
            r"monthly[:\s]*rp?\s*(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    min_str = match.group(1).replace(".", "").replace(",", "")
                    min_salary = int(min_str)
                    
                    max_str = match.group(2) if match.lastindex >= 2 else None
                    if max_str:
                        max_salary = int(max_str.replace(".", "").replace(",", ""))
                    else:
                        max_salary = min_salary
                    
                    return min_salary, max_salary, "IDR"
                except (ValueError, IndexError):
                    continue
        
        return None, None, "IDR"

    def extract_company_name(self, text: str) -> Optional[str]:
        """
        Extract company name from text.
        
        Args:
            text: Text containing company name
            
        Returns:
            str: Extracted company name or None
        """
        if not text:
            return None
        
        # Common patterns for company name extraction
        patterns = [
            r"(?:company|employer|business)[:\s]*([A-Z][A-Za-z\s&]+?)(?:\s*[-|]|\s*$)",
            r"(?:at|with)\s+([A-Z][A-Za-z\s&]+?)(?:\s*[-|]|\s*$)",
            r"^(?: hiring| vacancy)[^a-z]+([A-Z][A-Za-z\s&]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                company = match.group(1).strip()
                if len(company) > 2 and len(company) < 100:
                    return company
        
        return None

    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from text.
        
        Args:
            text: Text containing location
            
        Returns:
            str: Extracted location or None
        """
        if not text:
            return None
        
        # Indonesian location patterns
        location_patterns = [
            r"(?:location|based in|located)[:\s]*([A-Za-z\s]+?)(?:\s*[-|]|\s*$)",
            r"([A-Za-z]+(?:\s+[A-Za-z]+)?)\s*[-–—]\s*(?:Indonesia|ID)",
            r"(?:in|at)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)(?:\s*[-|]|\s*$)",
        ]
        
        # Common Indonesian cities
        cities = [
            "Jakarta", "Surabaya", "Bandung", "Bekasi", "Tangerang",
            "Karawang", "Bogor", "Depok", "Yogyakarta", "Semarang",
            "Medan", "Makassar", "Bali", "Kalimantan", "Sumatera",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:
                    return location
        
        # Fallback: search for known cities
        for city in cities:
            if city.lower() in text.lower():
                return city
        
        return None