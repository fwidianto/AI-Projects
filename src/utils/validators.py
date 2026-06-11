"""Input validation utilities."""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
    
    pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
    return bool(re.match(pattern, url))


def validate_salary_range(
    salary_min: Optional[int],
    salary_max: Optional[int],
) -> Tuple[bool, Optional[str]]:
    """
    Validate salary range.
    
    Args:
        salary_min: Minimum salary
        salary_max: Maximum salary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if salary_min is not None and salary_min < 0:
        return False, "Minimum salary cannot be negative"
    
    if salary_max is not None and salary_max < 0:
        return False, "Maximum salary cannot be negative"
    
    if salary_min is not None and salary_max is not None:
        if salary_min > salary_max:
            return False, "Minimum salary cannot exceed maximum salary"
    
    return True, None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (Indonesian format).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    
    # Check for valid Indonesian phone patterns
    patterns = [
        r"^\+62\d{9,12}$",  # +6281234567890
        r"^0\d{9,12}$",     # 081234567890
        r"^62\d{9,12}$",    # 6281234567890
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)


def validate_url_slug(slug: str) -> bool:
    """
    Validate URL slug format.
    
    Args:
        slug: Slug to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not slug:
        return False
    
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return bool(re.match(pattern, slug))


def validate_job_title(title: str) -> Tuple[bool, Optional[str]]:
    """
    Validate job title.
    
    Args:
        title: Job title to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or len(title.strip()) == 0:
        return False, "Job title cannot be empty"
    
    if len(title) < 3:
        return False, "Job title must be at least 3 characters"
    
    if len(title) > 200:
        return False, "Job title cannot exceed 200 characters"
    
    return True, None


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input by removing dangerous characters.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (truncate if exceeded)
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Normalize whitespace
    text = " ".join(text.split())
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate job search query.
    
    Args:
        query: Search query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or len(query.strip()) == 0:
        return False, "Search query cannot be empty"
    
    if len(query) < 2:
        return False, "Search query must be at least 2 characters"
    
    if len(query) > 200:
        return False, "Search query cannot exceed 200 characters"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Invalid characters in search query"
    
    return True, None