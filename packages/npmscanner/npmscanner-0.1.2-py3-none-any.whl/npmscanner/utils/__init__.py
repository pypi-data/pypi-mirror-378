"""
Crimson7 NPM Security Scanner - Utilities Module

This module contains utility functions and classes for the scanner.
"""

from .colors import Colors, ColorOutput
from .config import load_malicious_packages

__all__ = ['Colors', 'ColorOutput', 'load_malicious_packages']
