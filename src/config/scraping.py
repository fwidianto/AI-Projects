"""Scraping configuration."""

from dataclasses import dataclass, field
from typing import List, Dict
import random
import time


@dataclass
class ScraperConfig:
    """Configuration for a job board scraper."""

    name: str
    base_url: str
    enabled: bool = True
    rate_limit: float = 1.0  # seconds between requests
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "Job Intelligence Platform/1.0 (Educational Use)"
    headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Set default headers if not provided."""
        if not self.headers:
            self.headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
            }


# Pre-configured scrapers
SCRAPER_CONFIGS: Dict[str, ScraperConfig] = {
    "indeed": ScraperConfig(
        name="Indeed",
        base_url="https://www.indeed.com",
        rate_limit=2.0,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    ),
    "glints": ScraperConfig(
        name="Glints",
        base_url="https://glints.com",
        rate_limit=3.0,
    ),
    "jobstreet": ScraperConfig(
        name="JobStreet",
        base_url="https://www.jobstreet.com",
        rate_limit=3.0,
    ),
    "linkedin": ScraperConfig(
        name="LinkedIn",
        base_url="https://www.linkedin.com",
        enabled=False,  # Requires API authentication
        rate_limit=5.0,
    ),
}


# Search query templates
SEARCH_QUERIES = {
    "erp_analyst": [
        "ERP Analyst",
        "SAP Analyst",
        "Odoo Analyst",
        "ERP Consultant",
        "SAP Consultant",
    ],
    "business_analyst": [
        "Business Analyst",
        "BA",
        "Functional Consultant",
        "Requirements Analyst",
    ],
    "operations_analyst": [
        "Operations Analyst",
        "Process Analyst",
        "Operations Excellence",
        "Process Improvement",
    ],
    "finance_analyst": [
        "Finance Analyst",
        "Cost Analyst",
        "Budget Analyst",
        "Cost Control",
        "Financial Planning",
    ],
    "data_analyst": [
        "Data Analyst",
        "Reporting Analyst",
        "BI Analyst",
        "SQL Analyst",
        "Analytics Engineer",
    ],
}


# Location filters
LOCATION_FILTERS = {
    "jakarta": ["Jakarta", "JK", "Greater Jakarta", "DKI Jakarta"],
    "bekasi": ["Bekasi", "Bekasi Regency"],
    "karawang": ["Karawang", "Karawang Regency"],
    "remote": ["Remote", "Work from Home", "Hybrid", "WFH"],
}


# Salary range (IDR)
SALARY_RANGE = {
    "min": 15_000_000,  # 15M
    "max": 25_000_000,  # 25M
    "currency": "IDR",
}


def get_random_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> float:
    """Generate random delay to avoid detection."""
    return random.uniform(min_delay, max_delay)


def respect_rate_limit(scraper_name: str) -> None:
    """Sleep to respect rate limiting."""
    if scraper_name in SCRAPER_CONFIGS:
        delay = SCRAPER_CONFIGS[scraper_name].rate_limit
        time.sleep(delay + get_random_delay())
    else:
        time.sleep(1 + get_random_delay())


def get_search_url(scraper_name: str, query: str, location: str = "") -> str:
    """
    Generate search URL for a scraper.
    
    Args:
        scraper_name: Name of the scraper
        query: Job search query
        location: Location filter
        
    Returns:
        str: Formatted search URL
    """
    base_urls = {
        "indeed": "https://www.indeed.com/jobs?q={query}&l={location}",
        "glints": "https://glints.com/id/lowongan-kerja/?query={query}&location={location}",
        "jobstreet": "https://www.jobstreet.com/id/en/job-search/{query}-jobs-in-{location}/",
    }
    
    if scraper_name in base_urls:
        url = base_urls[scraper_name].format(
            query=query.replace(" ", "+"),
            location=location.replace(" ", "+") if location else "",
        )
        return url
    
    return ""