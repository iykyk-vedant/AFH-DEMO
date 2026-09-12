"""
User profile management service.
"""

from typing import Dict, Any, Optional

USER_DATABASE: Dict[str, Dict[str, Any]] = {
    "USR-101": {"name": "Alice Smith", "email": "alice@example.com", "phone": "123-456-7890"},
    "USR-102": {"name": "Bob Jones", "email": "bob@example.com", "phone": None},
}


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update user profile fields."""
    if user_id not in USER_DATABASE:
        raise KeyError(f"User {user_id} not found")

    user = USER_DATABASE[user_id]
    if "name" in updates:
        user["name"] = updates["name"].strip()

    # BUG (INC-006): Calls .strip() on phone without checking if phone is None or omitted
    if "phone" in updates:
        user["phone"] = updates["phone"].strip()

    return user
