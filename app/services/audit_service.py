"""
Security audit and event logging service.
"""

import json
import uuid
from typing import Dict, Any


def format_audit_log(event_id: uuid.UUID, action: str, actor: str) -> str:
    """Format and serialize an audit event record to JSON."""
    event_payload = {
        # BUG (INC-007): Passing raw uuid.UUID object to json.dumps raises TypeError
        "event_id": event_id,
        "action": action,
        "actor": actor,
    }
    return json.dumps(event_payload, default=str)
