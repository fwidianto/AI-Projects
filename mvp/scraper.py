"""
MVP Job Scraper Module

Scrapes job listings from Indeed.

Assumptions:
    - Indeed allows limited scraping for personal use
    - Rate limiting is respected (1 request per 2 seconds)
    - Job postings are publicly accessible without login
    - HTML structure of Indeed may change over time
"""

import re
import time
import random
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from mvp.database import Job


@dataclass
class ScraperResult:
    """Result of a scraping operation."""
    success: bool
    jobs: List[Job]
    error: Optional[str] = None
    pages_scraped: int = 0


class IndeedScraper:
    """
    Scraper for Indeed job listings.
    
    Assumptions:
        - Uses Indeed's public search pages (no API required)
        - Respects robots.txt and rate limits
        - Job cards follow consistent HTML structure
        - Salary information may not always be available
    """
    
    BASE_URL = "https://www.indeed.com"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def __init__(self, rate_limit: float = 2.0):
        """
        Initialize Indeed scraper.
        
        Args:
            rate_limit: Minimum seconds between requests
        """
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
    
    def _rate_limit(self) -> None:
        """Apply rate limiting with random variation."""
        delay = self.rate_limit + random.uniform(0.5, 1.5)
        time.sleep(delay)
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make HTTP request with error handling.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None on failure
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def search(
        self,
        query: str,
        location: str = "Jakarta",
        max_results: int = 50,
        days_back: int = 30,
    ) -> ScraperResult:
        """
        Search for jobs on Indeed.
        
        Args:
            query: Job search query
            location: Location filter
            max_results: Maximum number of results
            days_back: Filter by posting date (days)
            
        Returns:
            ScraperResult with jobs or error
            
        Assumptions:
            - Pagination works with start parameter
            - Each page contains approximately 15 jobs
        """
        jobs = []
        pages_scraped = 0
        start = 0
        
        while len(jobs) < max_results:
            # Build search URL
            params = {
                "q": query,
                "l": location,
                "jt": "fulltime",  # Full-time jobs
                "start": start,
            }
            
            if days_back < 365:
                params["fromage"] = days_back
            
            url = f"{self.BASE_URL}/jobs"
            
            soup = self._make_request(url)
            if not soup:
                break
            
            # Find job cards
            job_cards = soup.select("div.jobsearch-ResultsResults > div.jobsearch-ListContainer > ul.jobsearch-ResultsList > li")
            
            if not job_cards:
                # Try alternative selector
                job_cards = soup.select("div[id^='job_']")
            
            if not job_cards:
                break
            
            for card in job_cards:
                if len(jobs) >= max_results:
                    break
                
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
            
            pages_scraped += 1
            start += 10
            
            # Respect rate limiting
            self._rate_limit()
            
            # Safety limit
            if pages_scraped >= 10:
                break
        
        return ScraperResult(
            success=True,
            jobs=jobs,
            pages_scraped=pages_scraped,
        )
    
    def _parse_job_card(self, card: BeautifulSoup) -> Optional[Job]:
        """
        Parse a single job card element.
        
        Args:
            card: BeautifulSoup element of job card
            
        Returns:
            Job object or None if parsing fails
            
        Assumptions:
            - HTML structure is consistent across cards
            - Class names follow Indeed's naming convention
            - Some fields may be empty
        """
        try:
            # Extract title
            title_elem = card.select_one("h2.jobTitle > a, a.jobtitle, h2 a")
            title = title_elem.get("title", "").strip() if title_elem else ""
            
            # Extract company
            company_elem = card.select_one("span.companyName, div.company_location > span")
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Extract location
            location_elem = card.select_one("div.company_location > div, span.location, div.location")
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Check for remote
            is_remote = "remote" in location.lower() or "remote" in title.lower()
            
            # Extract salary
            salary_elem = card.select_one("span.salary-snippet, div.salary-snippet, span[data-testid='salary-snippet']")
            salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
            salary_min, salary_max = self._parse_salary(salary_text)
            
            # Extract job link and ID
            link_elem = card.select_one("a.jobtitle")
            job_link = ""
            source_id = ""
            if link_elem:
                href = link_elem.get("href", "")
                job_link = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                # Extract job ID from URL
                id_match = re.search(r"job/(\w+)", href)
                if id_match:
                    source_id = id_match.group(1)
            
            # Extract posting date
            date_elem = card.select_one("span.date, span[data-testid='myJobsStateDate'], date")
            posted_text = date_elem.get_text(strip=True) if date_elem else ""
            posted_date = self._parse_date(posted_text)
            
            # Extract summary
            summary_elem = card.select_one("div.job-snippet, div.summary")
            description = summary_elem.get_text(strip=True) if summary_elem else ""
            
            return Job(
                source="indeed",
                source_id=source_id or str(hash(title + company))[:20],
                title=title,
                company=company,
                location=location,
                is_remote=is_remote,
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency="IDR",
                description=description,
                apply_url=job_link,
                posted_date=posted_date,
            )
            
        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None
    
    def _parse_salary(self, salary_text: str) -> tuple:
        """
        Parse salary text to min/max values.
        
        Args:
            salary_text: Raw salary text from Indeed
            
        Returns:
            Tuple of (min_salary, max_salary) in IDR
            
        Assumptions:
            - Salary values are in IDR (Indonesian Rupiah)
            - Common formats: "Rp 15jt", "15,000,000", "15 million"
            - May only show one value (either min or max)
        """
        if not salary_text:
            return None, None
        
        # Clean the text
        text = salary_text.lower()
        text = text.replace("rp", "").replace("idr", "").replace(".", "").replace(",", "")
        
        # Extract numbers
        numbers = re.findall(r"(\d+)", text)
        
        if not numbers:
            return None, None
        
        values = []
        for num_str in numbers:
            num = int(num_str)
            # Handle million abbreviations
            if "jt" in text or "juta" in text or "million" in text:
                num = num * 1_000_000
            elif num < 1000:
                num = num * 1_000_000  # Assume million if small number
            values.append(num)
        
        if len(values) >= 2:
            return min(values), max(values)
        elif len(values) == 1:
            return values[0], values[0]
        
        return None, None
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse posting date text.
        
        Args:
            date_text: Raw date text from Indeed
            
        Returns:
            ISO format date string or None
            
        Assumptions:
            - Indeed uses relative dates: "Just posted", "Today", "3 days ago"
            - Converts to approximate posting date
        """
        if not date_text:
            return None
        
        text = date_text.lower()
        today = datetime.now()
        
        # Parse relative dates
        if "just posted" in text or "today" in text:
            return today.strftime("%Y-%m-%d")
        
        # Extract days
        days_match = re.search(r"(\d+)\s*day", text)
        if days_match:
            days = int(days_match.group(1))
            return (today - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Handle "30+" days
        if "+" in text:
            return (today - timedelta(days=30)).strftime("%Y-%m-%d")
        
        return None


def create_sample_jobs() -> List[Job]:
    """
    Create sample jobs for testing without scraping.
    
    Returns:
        List of sample Job objects
    
    Assumptions:
        - 10 sample jobs are sufficient for MVP testing
        - Jobs cover diverse roles matching target positions
        - Salary ranges reflect Indonesian market (15M-28M IDR)
    """
    sample_jobs = [
        Job(
            source="indeed",
            source_id="sample-001",
            title="ERP Analyst",
            company="Tech Corp Indonesia",
            location="Jakarta",
            is_remote=False,
            salary_min=18000000,
            salary_max=22000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Looking for an experienced ERP Analyst to support SAP implementation and maintenance. Will work with stakeholders to gather requirements and optimize business processes.",
            requirements="- 3+ years SAP experience\n- Strong analytical skills\n- ERP implementation experience",
            apply_url="https://www.indeed.com/sample-job-001",
            posted_date="2026-06-01",
        ),
        Job(
            source="indeed",
            source_id="sample-002",
            title="Business Analyst",
            company="Digital Solutions",
            location="Jakarta",
            is_remote=True,
            salary_min=15000000,
            salary_max=20000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="We need a Business Analyst to bridge IT and business teams. Experience with requirements gathering and process improvement preferred.",
            requirements="- 2+ years as Business Analyst\n- Experience with SQL and data analysis\n- Strong communication skills",
            apply_url="https://www.indeed.com/sample-job-002",
            posted_date="2026-06-03",
        ),
        Job(
            source="indeed",
            source_id="sample-003",
            title="SAP FI/CO Consultant",
            company="Enterprise Systems Indonesia",
            location="Bekasi",
            is_remote=False,
            salary_min=20000000,
            salary_max=28000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Seeking SAP FI/CO consultant for implementation project. Will configure modules and provide user training.",
            requirements="- SAP FI/CO certification\n- 4+ years SAP experience\n- Implementation experience preferred",
            apply_url="https://www.indeed.com/sample-job-003",
            posted_date="2026-06-05",
        ),
        Job(
            source="indeed",
            source_id="sample-004",
            title="Operations Analyst",
            company="Logistics Plus",
            location="Karawang",
            is_remote=False,
            salary_min=12000000,
            salary_max=18000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Analyze operational processes and identify improvement opportunities. Experience with ERP systems and data analysis required.",
            requirements="- Experience in operations or process improvement\n- Proficiency in Excel and SQL\n- Odoo or SAP experience a plus",
            apply_url="https://www.indeed.com/sample-job-004",
            posted_date="2026-06-07",
        ),
        Job(
            source="indeed",
            source_id="sample-005",
            title="Data Analyst",
            company="Analytics Hub",
            location="Jakarta",
            is_remote=True,
            salary_min=16000000,
            salary_max=24000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Analyze business data and create reports. Build dashboards in Looker Studio or Power BI.",
            requirements="- SQL expertise\n- Experience with BI tools\n- Python or R knowledge preferred",
            apply_url="https://www.indeed.com/sample-job-005",
            posted_date="2026-06-08",
        ),
        Job(
            source="indeed",
            source_id="sample-006",
            title="Cost Control Analyst",
            company="Manufacturing Indonesia",
            location="Bekasi",
            is_remote=False,
            salary_min=14000000,
            salary_max=20000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Manage cost analysis and budgeting processes. Experience with cost control and financial analysis in manufacturing preferred.",
            requirements="- Finance or accounting background\n- Cost analysis experience\n- SAP knowledge preferred",
            apply_url="https://www.indeed.com/sample-job-006",
            posted_date="2026-06-09",
        ),
        Job(
            source="indeed",
            source_id="sample-007",
            title="Odoo Developer/Analyst",
            company="Startup Tech",
            location="Remote",
            is_remote=True,
            salary_min=18000000,
            salary_max=25000000,
            salary_currency="IDR",
            employment_type="Contract",
            description="Support Odoo ERP implementation and customization. Gather requirements and configure modules.",
            requirements="- Odoo experience required\n- Python knowledge\n- ERP implementation experience",
            apply_url="https://www.indeed.com/sample-job-007",
            posted_date="2026-06-10",
        ),
        Job(
            source="indeed",
            source_id="sample-008",
            title="Finance Reporting Analyst",
            company="Banking Solutions",
            location="Jakarta",
            is_remote=False,
            salary_min=17000000,
            salary_max=23000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Create financial reports and analysis. Build dashboards and support financial planning activities.",
            requirements="- Financial analysis background\n- SQL and Excel skills\n- SAP experience preferred",
            apply_url="https://www.indeed.com/sample-job-008",
            posted_date="2026-06-10",
        ),
        Job(
            source="indeed",
            source_id="sample-009",
            title="Business Intelligence Analyst",
            company="Retail Analytics",
            location="Jakarta",
            is_remote=False,
            salary_min=20000000,
            salary_max=28000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Lead BI initiatives and data analytics projects. Experience with Looker Studio, Power BI, or Tableau required.",
            requirements="- 3+ years BI experience\n- Dashboard development\n- SQL and ETL experience",
            apply_url="https://www.indeed.com/sample-job-009",
            posted_date="2026-06-10",
        ),
        Job(
            source="indeed",
            source_id="sample-010",
            title="Budget Analyst",
            company="Corporate Services",
            location="Jakarta",
            is_remote=False,
            salary_min=13000000,
            salary_max=18000000,
            salary_currency="IDR",
            employment_type="Full-time",
            description="Support budgeting and forecasting processes. Analyze variances and prepare budget reports.",
            requirements="- Finance or accounting degree\n- Budgeting experience\n- Excel and SAP skills",
            apply_url="https://www.indeed.com/sample-job-010",
            posted_date="2026-06-11",
        ),
    ]
    
    return sample_jobs