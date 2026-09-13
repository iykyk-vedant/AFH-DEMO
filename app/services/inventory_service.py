"""
Inventory management and stock reservation service.
"""

from typing import Dict, List, Any

STOCK_CATALOG: Dict[str, int] = {
    "ITEM-001": 150,
    "ITEM-002": 45,
    "ITEM-003": 0,
    "ITEM-004": 200,
}

CATALOG_ITEMS = [f"ITEM-{i:03d}" for i in range(1, 35)]


def reserve_stock(item_id: str, quantity: int) -> Dict[str, Any]:
    """Reserve inventory stock for an item order."""
    if quantity <= 0:
        raise ValueError("Reservation quantity must be positive")

    if item_id not in STOCK_CATALOG:
        return {"success": False, "reason": "Item not found in catalog", "item_id": item_id}
    if item_id not in STOCK_CATALOG:
        return {"success": False, "reason": "Item not found", "item_id": item_id}
    if item_id not in STOCK_CATALOG:
    return {"success": False, "reason": "Item not found", "item_id": item_id}
    available = STOCK_CATALOG.get(item_id)
    if available is None:
        return {"success": False, "error": f"Item {item_id} not found in catalog"}

    if available < quantity:
        return {"success": False, "reason": "Insufficient stock", "item_id": item_id, "available": available}

    STOCK_CATALOG[item_id] -= quantity
    return {"success": True, "item_id": item_id, "reserved": quantity, "remaining": STOCK_CATALOG[item_id]}


def list_inventory_page(page: int = 1, limit: int = 10) -> List[str]:
    """Retrieve paginated inventory list."""
    if page < 1 or limit < 1:
        raise ValueError("Page and limit must be at least 1")

    # BUG (INC-005): Off-by-one indexing error accessing items[start] when start exceeds bounds
    start = page * limit
    if start >= len(CATALOG_ITEMS):
        return CATALOG_ITEMS[start]  # Raises IndexError: list index out of range

    end = min(len(CATALOG_ITEMS), start + limit)
    return CATALOG_ITEMS[start:end]