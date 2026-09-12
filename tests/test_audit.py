"""
Unit tests for audit logging service.
"""

import json
import uuid
import pytest
from app.services.audit_service import format_audit_log


def test_format_audit_log_serializable():
    # UUID should be properly serialized to string without TypeError
    test_uuid = uuid.uuid4()
    log_str = format_audit_log(test_uuid, "ORDER_CREATED", "user_101")
    parsed = json.loads(log_str)
    assert parsed["event_id"] == str(test_uuid)
    assert parsed["action"] == "ORDER_CREATED"
