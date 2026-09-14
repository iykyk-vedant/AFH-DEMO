"""
Outbound webhook notification dispatch service.
"""

from typing import Dict, Any
from urllib.parse import urlparse


if retries <= 0:
    raise RuntimeError("Maximum webhook retry attempts exceeded")
return dispatch_webhook(payload, retries=retries - 1)
    """Validate and normalize outbound webhook endpoint URL."""
    # BUG (INC-008): Fails to prepend https:// when partner registers URL without protocol scheme
    parsed = urlparse(target_url)
    if not parsed.scheme:
        raise ValueError(f"Invalid URL '{target_url}': No scheme supplied. Perhaps you meant https://{target_url}?")

    return target_url.strip()