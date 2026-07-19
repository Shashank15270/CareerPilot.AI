import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.models.db_models import User, Resume
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import get_current_user
from app.schemas.db_schemas import UserSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# -------------------------------------------------------------
# Input/Output Schemas
# -------------------------------------------------------------

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Candidate email address")
    name: str = Field(..., description="Candidate display name")
    password: str = Field(..., min_length=6, description="Candidate password (min 6 chars)")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Candidate login email")
    password: str = Field(..., description="Candidate password")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None

class ApiSettingsUpdate(BaseModel):
    api_preferences: Dict[str, Any] = Field(..., description="Custom API configuration options")

class UserProfileResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    location: Optional[str]
    experience: Optional[str]
    skills: Optional[List[str]]
    preferred_roles: Optional[List[str]]
    api_preferences: Optional[Dict[str, Any]]
    resume_count: int
    saved_jobs_count: int


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user and returns JWT credentials."""
    logger.info(f"Registration request for email: {request.email}")
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
        
    # Create user
    hashed = hash_password(request.password)
    db_user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed,
        skills=[],
        preferred_roles=[],
        api_preferences={}
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database registration failed. Please try again."
        )

    # Generate tokens
    access = create_access_token({"sub": db_user.email})
    refresh = create_refresh_token({"sub": db_user.email})
    
    db_user.refresh_token = refresh
    db.commit()
    
    return {"access_token": access, "refresh_token": refresh}


@router.post("/login", response_model=TokenResponse)
def login(request: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and yields session JWTs."""
    logger.info(f"Login request for email: {request.email}")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password combination."
        )
        
    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})
    
    user.refresh_token = refresh
    db.commit()
    
    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Exchanges a valid refresh token for a fresh access token."""
    payload = decode_token(request.refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )
        
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user or user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token mismatch or revoked."
        )
        
    new_access = create_access_token({"sub": user.email})
    new_refresh = create_refresh_token({"sub": user.email})
    
    user.refresh_token = new_refresh
    db.commit()
    
    return {"access_token": new_access, "refresh_token": new_refresh}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revokes active token sessions for the logged in user."""
    logger.info(f"Logging out user: {current_user.email}")
    current_user.refresh_token = None
    db.commit()
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieves full candidate settings and database statistics summaries."""
    # Count user uploads and bookmarks
    resume_count = len(current_user.resumes)
    saved_jobs_count = len(current_user.saved_jobs)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "location": current_user.location,
        "experience": current_user.experience,
        "skills": current_user.skills or [],
        "preferred_roles": current_user.preferred_roles or [],
        "api_preferences": current_user.api_preferences or {},
        "resume_count": resume_count,
        "saved_jobs_count": saved_jobs_count
    }


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(request: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Updates candidate profile info including skills, location, and role settings."""
    logger.info(f"Updating profile details for user: {current_user.email}")
    
    if request.name is not None:
        current_user.name = request.name
    if request.location is not None:
        current_user.location = request.location
    if request.experience is not None:
        current_user.experience = request.experience
    if request.skills is not None:
        current_user.skills = request.skills
    if request.preferred_roles is not None:
        current_user.preferred_roles = request.preferred_roles
        
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile values."
        )
        
    return get_me(current_user)


@router.put("/api-settings")
def update_api_settings(request: ApiSettingsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Saves API query preferences in the candidate settings registry."""
    logger.info(f"Saving API preferences for user: {current_user.email}")
    current_user.api_preferences = request.api_preferences
    db.commit()
    return {"message": "API preferences saved successfully."}


@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Removes a specific resume upload file and cascades metadata deletion."""
    logger.info(f"User {current_user.email} requested deletion of resume ID {resume_id}")
    
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found or unauthorized."
        )
        
    # Attempt to delete file from disk if path exists
    try:
        disk_path = Path(resume.file_path)
        if disk_path.exists():
            disk_path.unlink()
            logger.info(f"Removed resume file from disk: {resume.file_path}")
    except Exception as fe:
        logger.error(f"Error removing resume file from disk: {fe}")

    # Delete database record (cascading deletes versions and AI reports automatically)
    db.delete(resume)
    db.commit()
    return {"message": "Resume and related history logs deleted successfully."}


@router.delete("/delete-account")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Permanently deletes the candidate user profile and cascades related logs."""
    logger.info(f"PERMANENT ACCOUNT DELETION requested for: {current_user.email}")
    
    # 1. Delete resume files on disk for this user first
    for resume in current_user.resumes:
        try:
            disk_path = Path(resume.file_path)
            if disk_path.exists():
                disk_path.unlink()
        except Exception:
            pass

    # 2. Delete user record (cascades database deletes cleanly)
    db.delete(current_user)
    db.commit()
