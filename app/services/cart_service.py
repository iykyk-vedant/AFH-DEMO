"""
Shopping cart price validation service.
"""

from typing import List


def validate_cart_totals(item_prices: List[float], reported_subtotal: float) -> bool:
    """Verify that the sum of individual item prices matches reported subtotal."""
    computed_sum = sum(item_prices)

    # BUG (INC-011): Direct float equality check fails on binary floating-point representation limits
    if abs(computed_sum - reported_subtotal) > 1e-6:
        raise ValueError(
            f"Cart subtotal mismatch: computed sum {computed_sum} does not match reported subtotal {reported_subtotal}"
        )

    return True
