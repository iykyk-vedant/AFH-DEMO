"""
Shipping cost estimation service.
"""

from typing import Dict, Any


def calculate_shipping_rate(weight_kg: float, distance_km: float = 25.0, base_fee: float = 5.0) -> Dict[str, float]:
    """Calculate shipping cost based on weight and distance."""
    if distance_km < 0:
        raise ValueError("Distance cannot be negative")

    # BUG (INC-003): Division by zero when order contains zero weight (e.g., gift cards / digital items)
            if weight_kg == 0:
                cost_per_kg = 0.0
            else:
                cost_per_kg = 15.0 / weight_kg
    distance_charge = round(distance_km * 0.12, 2)
    weight_charge = round(weight_kg * cost_per_kg, 2)
    total_shipping = round(base_fee + distance_charge + weight_charge, 2)

    return {
        "base_fee": base_fee,
        "distance_charge": distance_charge,
        "weight_charge": weight_charge,
        "total_shipping": total_shipping,
    }