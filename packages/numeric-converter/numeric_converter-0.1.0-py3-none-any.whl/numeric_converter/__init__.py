"""
Numeric Converter - A Python package for converting Roman numerals and written numbers to integers.

This package provides simple functions to convert:
- Roman numerals (I, V, X, L, C, D, M) to integers
- Written numbers ("one", "two", etc.) to integers
"""

from .converter import roman_to_int, written_number_to_int

__version__ = "0.1.0"
__author__ = "Kaushika Semwal"
__email__ = "semwalkaushika@gmail.com"

# Make functions available at package level
__all__ = ["roman_to_int", "written_number_to_int"]