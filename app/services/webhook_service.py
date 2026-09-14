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
        # Automatically prepend https:// when scheme is missing
        target_url = f"https://{target_url}"
        parsed = urlparse(target_url)
    return target_urlrget_url}?")

    return target_url.strip()
