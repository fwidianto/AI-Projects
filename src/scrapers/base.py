"""Job scrapers package.

This package contains scrapers for various job boards.
Scrapers are not implemented yet - this is a placeholder.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseScraper(ABC):
    """Base class for all job scrapers."""

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url

    @abstractmethod
    def scrape(self, query: str, location: str = "") -> List[Dict[str, Any]]:
        """
        Scrape jobs based on query and location.
        
        Args:
            query: Job search query
            location: Location filter
            
        Returns:
            List of job dictionaries
        """
        pass

    @abstractmethod
    def parse_job(self, job_element) -> Dict[str, Any]:
        """
        Parse a single job element.
        
        Args:
            job_element: Raw job element from the page
            
        Returns:
            Dictionary with job data
        """
        pass

    def validate_job(self, job_data: Dict[str, Any]) -> bool:
        """
        Validate job data has required fields.
        
        Args:
            job_data: Job dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["title", "company", "source_id"]
        return all(field in job_data and job_data[field] for field in required_fields)


# Import will be implemented when scrapers are added
__all__ = ["BaseScraper"]