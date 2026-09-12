"""
Unit tests for authentication service.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_success():
    """
    Test login with valid credentials.
    This test will FAIL with TypeError until the bcrypt bug is fixed.
    """
    payload = {
        "email": "alex@shopstack.io",
        "password": "SuperSecretPassword123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "token" in data
