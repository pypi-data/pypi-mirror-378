"""
HeySol API Client Library
"""

from .client import HeySolClient
from .config import HeySolConfig
from .exceptions import HeySolError, ValidationError, AuthenticationError, ConnectionError, RateLimitError

__version__ = "1.1.0"
__all__ = [
    "HeySolClient",
    "HeySolConfig",
    "HeySolError",
    "ValidationError",
    "AuthenticationError",
    "ConnectionError",
    "RateLimitError",
]