"""
Unit tests for user service.
"""

import pytest
from app.services.user_service import update_user_profile


def test_update_name():
    updated = update_user_profile("USR-101", {"name": "Alice Cooper"})
    assert updated["name"] == "Alice Cooper"


def test_update_with_none_phone():
    # Updating profile with phone=None should not crash with AttributeError
    updated = update_user_profile("USR-102", {"name": "Bob Robert", "phone": None})
    assert updated["name"] == "Bob Robert"
    assert updated["phone"] is None
