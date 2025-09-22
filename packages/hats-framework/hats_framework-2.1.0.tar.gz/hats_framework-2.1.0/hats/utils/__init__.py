"""
Utils package for HATS framework.
Contains utility modules for logging, detection, etc.
"""

from .logger import get_logger
from .detector import ToolDetector

__all__ = ['get_logger', 'ToolDetector']
