import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.recommendation_engine import recommend_jobs
from app.auth.dependencies import get_current_user_optional
from app.models.db_models import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Base directory for uploads
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/")
async def root():
    """
    Status endpoint to check if the recommendation API is running.
    """
    logger.info("Status endpoint GET / reached.")
    return {
        "message": "Recommendation API Running"
    }


@router.post("/recommend")
async def recommend(
    resume: UploadFile = File(...),
    query: Optional[str] = Form(default=""),
    top_k: Optional[int] = Form(default=10),
    country: Optional[str] = Form(default=None),
    state: Optional[str] = Form(default=None),
    city: Optional[str] = Form(default=None),
    experience_level: Optional[str] = Form(default=None),
    employment_type: Optional[str] = Form(default=None),
    workplace_type: Optional[str] = Form(default=None),
    salary_min: Optional[int] = Form(default=None),
    company_name: Optional[str] = Form(default=None),
    skills: Optional[str] = Form(default=None),
    industry: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Endpoint to receive a resume file and optional search queries, run the recommendation engine,
    and return the top K matched jobs.
    """
    logger.info("Recommendation request received.")

    # Define allowed file extensions and MIME types
    allowed_extensions = {".pdf", ".docx"}
    allowed_content_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    # Extract filename and extension
    filename = resume.filename or "unnamed_resume"
    extension = Path(filename).suffix.lower()

    # If extension is empty, try to map from content-type header
    if not extension:
        if resume.content_type == "application/pdf":
            extension = ".pdf"
        elif resume.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extension = ".docx"

    # Validate file format
    is_valid = (
        extension in allowed_extensions or
        resume.content_type in allowed_content_types
    )

    if not is_valid:
        logger.warning(
            f"Invalid file format uploaded: {filename} with MIME type {resume.content_type}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF and DOCX files are accepted."
        )

    # Generate a unique name for the file to prevent collisions
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    destination_path = UPLOAD_DIR / unique_filename

    # Save file to disk
    try:
        logger.info(f"Saving uploaded resume to {destination_path}")
        with destination_path.open("wb") as buffer:
            while chunk := await resume.read(1024 * 1024):
                buffer.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save resume file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save the uploaded file: {str(e)}"
        )
    finally:
        # Release resource
        await resume.close()

    # JSearch is the only job source, so a missing key means zero results no
    # matter what. Fail loudly here rather than returning an empty list that
    # looks identical to "no jobs matched your filters".
    if not os.getenv("RAPIDAPI_KEY"):
        logger.error("RAPIDAPI_KEY is not configured; cannot fetch any jobs.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Job search is not configured on the server: RAPIDAPI_KEY is missing. "
                "Add it to backend/.env and restart the server."
            ),
        )

    # Call recommendation engine
    try:
        # Default or fallback values mapping
        query_str = query if query is not None else ""
        top_k_val = top_k if top_k is not None else 10

        logger.info(f"Invoking recommendation_engine for resume: {unique_filename} (query: '{query_str}', top_k: {top_k_val})")
        recommendations = await recommend_jobs(
            resume_path=str(destination_path.resolve()),
            query=query_str,
            top_k=top_k_val,
            db=db,
            user_id=current_user.id,
            country=country,
            state=state,
            city=city,
            experience_level=experience_level,
            employment_type=employment_type,
            workplace_type=workplace_type,
            salary_min=salary_min,
            company_name=company_name,
            skills=skills,
            industry=industry
        )
        logger.info("Job recommendation process completed successfully.")
        return recommendations

    except ValueError as ve:
        logger.warning(f"Validation error in recommendation: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except FileNotFoundError as fnfe:
        logger.error(f"Saved resume file disappeared or not found: {str(fnfe)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnfe)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in recommendation pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during recommendation processing: {str(e)}"
        )
