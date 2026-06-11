"""Helper utilities."""

import re
from typing import Optional, List
from datetime import datetime, timedelta


def format_currency(
    amount: int,
    currency: str = "IDR",
    include_symbol: bool = True,
) -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        include_symbol: Include currency symbol
        
    Returns:
        str: Formatted currency string
    """
    symbols = {
        "IDR": "Rp",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }
    
    symbol = symbols.get(currency, currency) if include_symbol else ""
    
    if currency == "IDR":
        # Format as millions (e.g., "15M")
        millions = amount / 1_000_000
        return f"{symbol}{millions:.0f}M"
    else:
        # Standard number formatting
        return f"{symbol}{amount:,.2f}"


def parse_salary(salary_text: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse salary text to min/max values.
    
    Args:
        salary_text: Salary text (e.g., "Rp 15.000.000 - 25.000.000")
        
    Returns:
        Tuple of (min_salary, max_salary) in IDR
    """
    if not salary_text:
        return None, None
    
    # Clean the text
    text = salary_text.lower()
    text = text.replace("rp", "").replace("idr", "").replace(".", "").replace(",", "")
    
    # Extract numbers
    numbers = re.findall(r"\d+", text)
    
    if not numbers:
        return None, None
    
    # Convert to integers (multiply by 1000 for 'M' suffix)
    values = []
    for num in numbers:
        if "juta" in text or "jt" in text or "jt" in text:
            values.append(int(num) * 1_000_000)
        elif len(num) <= 3:
            values.append(int(num) * 1000)
        else:
            values.append(int(num))
    
    if len(values) == 1:
        return values[0], values[0]
    elif len(values) >= 2:
        return min(values), max(values)
    
    return None, None


def clean_text(text: str) -> str:
    """
    Clean HTML/text by removing extra whitespace and special characters.
    
    Args:
        text: Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special Unicode characters
    text = text.encode("ascii", "ignore").decode("ascii")
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Find a good break point
    truncated = text[: max_length - len(suffix)]
    
    # Try to break at word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.7:  # Only break at word if reasonable
        truncated = truncated[:last_space]
    
    return truncated + suffix


def format_date(date: datetime, format_str: str = "%B %d, %Y") -> str:
    """
    Format date to a readable string.
    
    Args:
        date: Date to format
        format_str: strftime format string
        
    Returns:
        str: Formatted date string
    """
    if not date:
        return ""
    return date.strftime(format_str)


def time_ago(date: datetime) -> str:
    """
    Get human-readable time ago string.
    
    Args:
        date: Date to compare
        
    Returns:
        str: Time ago string (e.g., "2 days ago")
    """
    if not date:
        return "Unknown"
    
    now = datetime.utcnow()
    diff = now - date
    
    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < timedelta(days=30):
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"


def extract_skills_from_text(text: str, skill_patterns: List[str]) -> List[str]:
    """
    Extract skills from text using pattern matching.
    
    Args:
        text: Text to search
        skill_patterns: List of skill patterns to match
        
    Returns:
        List of matched skills
    """
    if not text or not skill_patterns:
        return []
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_patterns:
        # Check for exact word match (case insensitive)
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills


def normalize_location(location: str) -> str:
    """
    Normalize location names.
    
    Args:
        location: Location to normalize
        
    Returns:
        str: Normalized location
    """
    if not location:
        return ""
    
    location = location.strip()
    
    # Normalize common variations
    location_mappings = {
        "jakarta": "Jakarta",
        "jakarta raya": "Jakarta",
        "dki jakarta": "Jakarta",
        "jk": "Jakarta",
        "bekasi": "Bekasi",
        "karawang": "Karawang",
        "bandung": "Bandung",
        "surabaya": "Surabaya",
        "remote": "Remote",
        "work from home": "Remote",
        "wfh": "Remote",
        "hybrid": "Hybrid",
    }
    
    normalized = location_mappings.get(location.lower(), location)
    
    return normalized


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Don't cut in the middle of a word if possible
        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space > chunk_size * 0.8:
                chunk = chunk[:last_space]
                end = start + last_space
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def similarity_score(list1: List[str], list2: List[str]) -> float:
    """
    Calculate Jaccard similarity between two lists.
    
    Args:
        list1: First list
        list2: Second list
        
    Returns:
        float: Similarity score (0.0 - 1.0)
    """
    if not list1 or not list2:
        return 0.0
    
    set1 = set(s.lower() for s in list1)
    set2 = set(s.lower() for s in list2)
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0