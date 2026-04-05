"""
Time utilities - timestamp helpers.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import time


def utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def utc_timestamp() -> int:
    """Get current UTC timestamp in seconds."""
    return int(time.time())


def format_date(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format datetime to string."""
    if dt is None:
        return ""
    return dt.strftime(fmt)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def time_ago(dt: datetime) -> str:
    """Get human-readable time ago string."""
    if dt is None:
        return "unknown"
    
    now = utc_now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        return format_date(dt)


def get_date_path(dt: Optional[datetime] = None) -> str:
    """Get date path for storage (YYYY/MM/DD)."""
    if dt is None:
        dt = utc_now()
    return f"{dt.year}/{dt.month:02d}/{dt.day:02d}"


def get_hour_bucket(dt: Optional[datetime] = None) -> int:
    """Get hour bucket (0-23) for batching."""
    if dt is None:
        dt = utc_now()
    return dt.hour