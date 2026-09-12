"""
Unit tests for shipping rate calculation service.
"""

import pytest
from app.services.shipping_service import calculate_shipping_rate


def test_standard_shipping():
    res = calculate_shipping_rate(weight_kg=2.0, distance_km=50.0)
    assert res["total_shipping"] > 0


def test_digital_items_zero_weight_shipping():
    # Should not raise ZeroDivisionError for zero-weight digital orders
    res = calculate_shipping_rate(weight_kg=0.0, distance_km=10.0)
    assert res["weight_charge"] == 0.0
    assert res["total_shipping"] == 6.20
