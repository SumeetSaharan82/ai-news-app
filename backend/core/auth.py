"""
Authentication utilities for JWT token handling and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext
from backend.config.settings import get_settings

settings = get_settings()

# Password hashing context - use pbkdf2_sha256 for better compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT configuration
import os, logging as _logging
_DEFAULT_SECRET = "briefed-dev-secret-change-in-production"
SECRET_KEY = settings.secret_key or os.environ.get("SECRET_KEY", _DEFAULT_SECRET)
_insecure = SECRET_KEY in (_DEFAULT_SECRET, "your-secret-key-change-in-production")
if _insecure:
    if not settings.debug:
        raise RuntimeError(
            "SECRET_KEY is set to a known default value. "
            "Set a strong random SECRET_KEY in Replit Secrets before deploying."
        )
    _logging.getLogger(__name__).warning(
        "⚠️  Using default JWT secret — set SECRET_KEY in Replit Secrets before deploying!"
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_token_payload(token: str) -> Optional[dict]:
    """Extract user ID from JWT token"""
    payload = decode_access_token(token)
    if payload is None:
        return None
    return payload
