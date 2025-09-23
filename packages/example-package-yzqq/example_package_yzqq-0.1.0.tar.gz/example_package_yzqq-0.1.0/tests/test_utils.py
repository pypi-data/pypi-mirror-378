"""
Tests for the utils module.
"""

import pytest
from simple_package.utils import (
    format_number, validate_email, clean_string, 
    count_words, reverse_string
)


def test_format_number():
    """Test format_number function."""
    assert format_number(42) == "42"
    assert format_number(3.14159, 2) == "3.14"
    assert format_number(3.14159, 4) == "3.1416"
    assert format_number(10.0, 1) == "10.0"


def test_validate_email():
    """Test validate_email function."""
    assert validate_email("test@example.com") is True
    assert validate_email("user.name+tag@domain.co.uk") is True
    assert validate_email("invalid.email") is False
    assert validate_email("@example.com") is False
    assert validate_email("test@") is False
    assert validate_email("") is False


def test_clean_string():
    """Test clean_string function."""
    assert clean_string("  hello   world  ") == "hello world"
    assert clean_string("single") == "single"
    assert clean_string("") == ""
    assert clean_string("   ") == ""


def test_count_words():
    """Test count_words function."""
    assert count_words("hello world") == 2
    assert count_words("single") == 1
    assert count_words("") == 0  # empty string should have 0 words
    assert count_words("  multiple   spaces  between  ") == 3


def test_reverse_string():
    """Test reverse_string function."""
    assert reverse_string("hello") == "olleh"
    assert reverse_string("") == ""
    assert reverse_string("a") == "a"
    assert reverse_string("12345") == "54321"