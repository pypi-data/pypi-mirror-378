"""
Utility functions for the simple package.
"""

import re
from typing import Union


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """Format a number with specified precision."""
    if isinstance(number, int):
        return str(number)
    return f"{number:.{precision}f}"


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def clean_string(text: str) -> str:
    """Clean a string by removing extra whitespace."""
    return " ".join(text.split())


def count_words(text: str) -> int:
    """Count words in a text string."""
    if not text.strip():
        return 0
    return len(text.split())


def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]