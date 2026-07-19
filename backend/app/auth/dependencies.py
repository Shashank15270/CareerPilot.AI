from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.auth.jwt import decode_token

def get_token_from_header(request: Request) -> str:
    """
    Extracts Bearer token from Authorization request header.
    """
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        return ""
    try:
        scheme, credentials = authorization.split()
        if scheme.lower() == "bearer":
            return credentials
    except ValueError:
        pass
    return ""

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency to retrieve the currently logged in user.
    Raises 401 Unauthorized if authentication fails.
    """
    token = get_token_from_header(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Missing Authorization Header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token, expected_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency to retrieve current user if authenticated,
    otherwise falls back to the default seed user (ID = 1).
    """
    token = get_token_from_header(request)
    if token:
        payload = decode_token(token, expected_type="access")
        if payload:
            email = payload.get("sub")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return user
    
    # Fallback to seeded default user with ID = 1
    default_user = db.query(User).filter(User.id == 1).first()
    if not default_user:
        # Create seed user if database is unseeded
        default_user = User(
            id=1,
            email="default@example.com",
            name="Default User"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user
