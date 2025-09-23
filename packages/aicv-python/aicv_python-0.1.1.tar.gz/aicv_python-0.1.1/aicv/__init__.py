"""
AiCV Python SDK

A comprehensive AI-powered CV analysis and generation toolkit.
"""

__version__ = "0.1.1"
__author__ = "AIGility Cloud Innovation"
__email__ = "contact@aigility.com"
__description__ = "AI-powered CV analysis and generation toolkit"

from .client import AiCVClient
from .exceptions import AiCVError, AuthenticationError, APIError, ValidationError

__all__ = [
    "AiCVClient",
    "AiCVError", 
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
