"""
Simple Package - A demonstration package for uv packaging.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import Calculator, greet
from .utils import format_number

__all__ = ["Calculator", "greet", "format_number"]