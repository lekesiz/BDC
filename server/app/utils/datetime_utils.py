"""DateTime utility functions."""

from datetime import datetime
from typing import Optional, Union


def parse_datetime(date_str: Union[str, datetime, None]) -> Optional[datetime]:
    """Parse datetime from various formats.
    
    Args:
        date_str: Date string, datetime object, or None
        
    Returns:
        datetime object or None
    """
    if not date_str:
        return None
    
    if isinstance(date_str, datetime):
        return date_str
    
    # Try different date formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # If no format works, try ISO format
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        raise ValueError(f"Unable to parse datetime: {date_str}")


def parse_date(date_str: Union[str, datetime, None]) -> Optional[datetime]:
    """Parse date from various formats.
    
    Args:
        date_str: Date string, datetime object, or None
        
    Returns:
        datetime object (time set to midnight) or None
    """
    if not date_str:
        return None
    
    parsed = parse_datetime(date_str)
    if parsed:
        return datetime(parsed.year, parsed.month, parsed.day)
    
    return None


def format_datetime(dt: Optional[datetime], fmt: str = '%Y-%m-%d %H:%M') -> str:
    """Format datetime to string.
    
    Args:
        dt: datetime object
        fmt: Format string
        
    Returns:
        Formatted string or empty string if dt is None
    """
    if not dt:
        return ''
    
    return dt.strftime(fmt)


def format_date(dt: Optional[datetime], fmt: str = '%Y-%m-%d') -> str:
    """Format date to string.
    
    Args:
        dt: datetime object
        fmt: Format string
        
    Returns:
        Formatted string or empty string if dt is None
    """
    if not dt:
        return ''
    
    return dt.strftime(fmt)