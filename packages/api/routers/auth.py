# pyright: reportCallIssue=false
"""
Authentication router for user registration, login, and token management.
"""
from datetime import timedelta
from typing import cast, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, crud, config, dependencies
# Import auth functions explicitly to avoid module confusion
from ..auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Register a new user account.
    
    Args:
        user: User registration data (email, password, name)
        db: Database session
        
    Returns:
        UserPublic: Created user information (without password)
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        db_user = crud.create_user(db=db, user=user)
        return schemas.UserPublic(
            id=db_user.id,
            email=cast(str, db_user.email),
            name=cast(Optional[str], db_user.name)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=schemas.Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db)
):
    """
    Login with email and password to receive a JWT access token.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session
        
    Returns:
        Token: JWT access token and token type
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  
        expires_delta=access_token_expires
    )
    
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=schemas.UserPublic)
def get_current_user_info(
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Get information about the currently authenticated user.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        UserPublic: Current user information
    """
    return current_user
