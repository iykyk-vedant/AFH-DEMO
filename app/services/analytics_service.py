"""
Analytics and reporting query parameter parsing service.
"""

from typing import Optional


def parse_date_range_days(raw_param: Optional[str], default_days: int = 30) -> int:
    """Parse days query parameter into an integer range with default fallback."""
    if raw_param is None:
        return default_days

    # BUG (INC-009): Calling int() directly on empty string or whitespace raises ValueError
    return int(raw_param)
