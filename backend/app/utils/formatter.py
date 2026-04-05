"""
Formatter utilities - clean and normalize messages.
"""
import re
from typing import Optional
from html import escape


def clean_message(text: str, max_length: int = 4000) -> str:
    """
    Clean and sanitize message text.
    - Remove excessive whitespace
    - Limit length
    - Escape HTML
    """
    if not text:
        return ""
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Remove excessive internal whitespace (more than 2 spaces)
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove excessive newlines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Escape HTML to prevent XSS
    text = escape(text)
    
    return text


def normalize_content(content: str) -> str:
    """Normalize message content for storage/search."""
    # Lowercase for search indexing (optional)
    # Remove special characters for search (optional)
    return content.strip()


def format_timestamp(timestamp) -> str:
    """Format a timestamp for display."""
    from datetime import datetime
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M")
    return str(timestamp)


def truncate_text(text: str, max_len: int = 50) -> str:
    """Truncate text for previews."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."