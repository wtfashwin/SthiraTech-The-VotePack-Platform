import uuid
from typing import cast, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import database, schemas, auth, models

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    """
    Yields a new, isolated SQLAlchemy database session for each request.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> schemas.UserPublic:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        UserPublic schema with authenticated user data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    token_data = auth.decode_access_token(token)
    if token_data is None or token_data.user_id is None:
        raise credentials_exception
    
    # Fetch user from database
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    # Use cast to satisfy type checker while accessing SQLAlchemy model attributes
    return schemas.UserPublic(
        id=user.id,
        email=cast(str, user.email),
        name=cast(Optional[str], user.name)
    )

