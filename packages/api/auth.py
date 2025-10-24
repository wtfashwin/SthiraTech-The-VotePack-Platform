"""
Authentication utilities for JWT token generation and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
import hashlib
from jose import JWTError, jwt

import config
import schemas

# Simple password hashing using SHA-256 (no bcrypt complications)
def get_password_hash(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[schemas.TokenData]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData object if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None or not isinstance(user_id_str, str):
            return None
        # Convert string UUID back to UUID object
        user_id = uuid.UUID(user_id_str)
        return schemas.TokenData(user_id=user_id)
    except JWTError:
        return None
    except ValueError:  # Invalid UUID format
        return None
