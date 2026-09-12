"""
Unit tests for inventory service.
"""

import pytest
from app.services.inventory_service import reserve_stock, list_inventory_page


def test_reserve_stock_existing_item():
    res = reserve_stock("ITEM-001", 5)
    assert res["success"] is True


def test_reserve_stock_missing_item():
    # Should safely return failure for missing items without raising KeyError
    res = reserve_stock("ITEM-999_UNKNOWN", 1)
    assert res["success"] is False
    assert "not found" in res.get("reason", "").lower()


def test_list_inventory_out_of_bounds():
    # Last page or beyond should return an empty list, not crash with IndexError
    page_beyond = list_inventory_page(page=10, limit=10)
    assert page_beyond == []
