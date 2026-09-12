"""
Unit tests for outbound webhook service.
"""

import pytest
from app.services.webhook_service import prepare_webhook_target


def test_prepare_webhook_with_scheme():
    res = prepare_webhook_target("https://api.partner.com/events")
    assert res == "https://api.partner.com/events"


def test_prepare_webhook_without_scheme():
    # Schemeless URL should be automatically normalized to https://
    res = prepare_webhook_target("api.partner.com/events")
    assert res == "https://api.partner.com/events"
