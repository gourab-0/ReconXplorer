from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


import re
import secrets
import hashlib

# -----------------------------
# SECURITY UTILS
# -----------------------------
def hash_token(token: str) -> str:
    """Hash a token for secure database storage."""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_csrf_token() -> str:
    """Generate a random CSRF token."""
    return secrets.token_urlsafe(32)

def validate_password_complexity(password: str) -> bool:
    """
    Validate password complexity:
    - Min 10 chars
    - At least one number
    - At least one letter
    - At least one symbol
    """
    if len(password) < 10:
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[a-zA-Z]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------
# JWT UTILS
# -----------------------------
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt

def create_refresh_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(days=7) # Refresh token lasts 7 days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str):
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )