"""
Payment and checkout calculation service.
"""

from typing import Dict, Any, Optional

DISCOUNT_CODES = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,
    "VIP50": 0.50,
}


def calculate_discount(subtotal: float, discount_code: Optional[str] = None) -> float:
    """Calculate the discount dollar amount."""
    if not discount_code:
        return 0.0
    rate = DISCOUNT_CODES.get(discount_code.upper(), 0.0)
    return round(subtotal * rate, 2)


def process_order_total(subtotal: float, discount_code: Optional[str] = None, tax_rate: float = 0.08) -> Dict[str, float]:
    """Calculate the final total including discount and tax."""
    discount = calculate_discount(subtotal, discount_code)
        # BUG (INC-002): Discount is mistakenly subtracted twice from subtotal
        discounted_subtotal = max(0.0, subtotal - discount)
    tax = round(discounted_subtotal * tax_rate, 2)
    total = round(discounted_subtotal + tax, 2)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
    }