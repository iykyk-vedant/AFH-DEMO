"""
Unit tests for analytics service.
"""

import pytest
from app.services.analytics_service import parse_date_range_days


def test_parse_valid_days():
    assert parse_date_range_days("7") == 7
    assert parse_date_range_days("90") == 90


def test_parse_empty_string_fallback():
    # Empty string should fall back to default, not crash with ValueError
    assert parse_date_range_days("") == 30
    assert parse_date_range_days("   ") == 30
