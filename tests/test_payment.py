"""
Unit tests for payment calculation service.
"""

from app.services.payment_service import calculate_discount, process_order_total


def test_calculate_discount():
    assert calculate_discount(100.0, "SAVE10") == 10.0
    assert calculate_discount(100.0, "SAVE20") == 20.0
    assert calculate_discount(100.0, "VIP50") == 50.0
    assert calculate_discount(100.0, None) == 0.0


def test_process_order_total():
    res = process_order_total(100.0, "SAVE20", tax_rate=0.08)
    assert res["subtotal"] == 100.0
    assert res["discount"] == 20.0
    assert res["tax"] == 6.40
    assert res["total"] == 86.40
