"""
Outbound webhook notification dispatch service.
"""

from typing import Dict, Any
from urllib.parse import urlparse


def prepare_webhook_target(target_url: str) -> str:
    """Validate and normalize outbound webhook endpoint URL."""
    # BUG (INC-008): Fails to prepend https:// when partner registers URL without protocol scheme
    parsed = urlparse(target_url)
    if not parsed.scheme:
        raise ValueError(f"Invalid URL '{target_url}': No scheme supplied. Perhaps you meant https://{target_url}?")

    return target_url.strip()
