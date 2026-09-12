"""
Unit tests for rate limiter client IP extraction.
"""

import pytest
from app.services.rate_limiter import extract_client_ip


def test_extract_client_ip_with_header():
    ip = extract_client_ip({"x-forwarded-for": "203.0.113.195, 70.41.3.18"})
    assert ip == "203.0.113.195"


def test_extract_client_ip_without_header():
    # Direct internal traffic without x-forwarded-for should default to 127.0.0.1 without KeyError
    ip = extract_client_ip({"host": "api.internal"})
    assert ip == "127.0.0.1"
