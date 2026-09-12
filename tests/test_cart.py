"""
Unit tests for shopping cart price validation.
"""

import pytest
from app.services.cart_service import validate_cart_totals


def test_validate_simple_integers():
    assert validate_cart_totals([10.0, 20.0, 30.0], 60.0) is True


def test_validate_floating_point_prices():
    # 10.10 + 20.20 = 30.299999999999997 in standard IEEE-754 floats
    # Should validate as equal when rounded to standard cents (2 decimal places)
    assert validate_cart_totals([10.10, 20.20], 30.30) is True
