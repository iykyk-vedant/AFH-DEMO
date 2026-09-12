"""
Request rate limiting and client IP extraction service.
"""

from typing import Dict, Optional


def extract_client_ip(headers: Dict[str, str]) -> str:
    """Extract client IP address from HTTP request headers."""
    # BUG (INC-010): Directly indexing headers dictionary throws KeyError when x-forwarded-for is missing
    forwarded_for = headers["x-forwarded-for"]
    return forwarded_for.split(",")[0].strip()
