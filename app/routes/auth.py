"""
Authentication router for user login and token issuance.
"""

import bcrypt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class MockUser:
    def __init__(self, user_id: str, email: str, password_hash: str):
        self.id = user_id
        self.email = email
        self.password_hash = password_hash  # Stored as string in database


# Simulated database of registered users
# Password: "SuperSecretPassword123!"
USERS_DB = {
    "alex@shopstack.io": MockUser(
        user_id="usr_001",
        email="alex@shopstack.io",
        password_hash="$2b$12$e8Y0w/QW4V93D7kQ2J0p0eF5jZ8gZ6xZ4aK7cQ2jV0zK1aP0xO0q."
    )
}


@router.post("/login")
def login(payload: LoginRequest):
    """
    Authenticate user with email and password.
    """
    user = USERS_DB.get(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # BUG (Line 42): bcrypt.checkpw expects both arguments to be bytes.
    # payload.password is encoded to bytes, but user.password_hash is a str,
    # causing a TypeError: a bytes-like object is required, not 'str'
    is_valid = bcrypt.checkpw(
        payload.password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {
        "status": "success",
        "user_id": user.id,
        "token": f"jwt_mock_token_{user.id}"
    }
