"""GitHub Security Advisory (GHSA) client library.

A Python library for interacting with the GitHub Security Advisory API,
providing structured access to security advisory data.

Main exports:
- GHSAClient: Main client for interacting with the GHSA API
- Advisory: Main model representing a GitHub Security Advisory
- GHSA_ID: Type-safe GHSA identifier with validation
- CVE_ID: Type-safe CVE identifier with validation
- RateLimitExceeded: Exception raised when API rate limit is exceeded
"""

from .client import GHSAClient
from .models import Advisory, GHSA_ID, CVE_ID
from .exceptions import RateLimitExceeded

__version__ = "0.1.0"
__all__ = ["GHSAClient", "Advisory", "GHSA_ID", "CVE_ID", "RateLimitExceeded"]
