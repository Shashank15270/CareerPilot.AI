import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user_optional
from app.models.db_models import User
from app.services.llm_service import (
    review_resume,
    analyze_job_match,
    analyze_skill_gap,
    prepare_interview,
    start_mock_interview_session,
    submit_mock_interview_answer,
    provide_career_advice
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Base uploads folder
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"

# -------------------------------------------------------------
# Request Schemas
# -------------------------------------------------------------

class JobDetailsSchema(BaseModel):
    title: str = Field(..., description="The job title")
    company: str = Field(..., description="The hiring company name")
    description: str = Field(..., description="The full job description")
    similarity_score: Optional[float] = Field(0.0, description="The similarity score from matching engine")

class MockInterviewStartRequest(BaseModel):
    title: str = Field(..., description="Target job title")
    company: str = Field(..., description="Target job company")
    description: str = Field(..., description="Target job description")

class MockInterviewAnswerRequest(BaseModel):
    session_id: str = Field(..., description="The active interview session UUID")
    answer: str = Field(..., description="The candidate's response to the question")


# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------

def get_latest_resume_context() -> dict:
    """
    Utility function to retrieve the cached parsed resume details.
    """
    latest_path = UPLOAD_DIR / "latest_resume.json"
    if not latest_path.exists():
        logger.warning(f"No resume cached at {latest_path}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume found on backend. Please upload a resume first to generate job recommendations."
        )
    
    try:
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read cached resume JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while loading your profile: {str(e)}"
        )


def get_latest_resume_version_context(db: Session, user_id: int = 1) -> tuple[int, dict, str]:
    """
    Utility function to retrieve the latest version database ID, parsed details, and raw text for a specific user.
    Migrates the latest disk-cached resume to database dynamically on first call.
    """
    from app.repository.db_repository import JobSearchRepository
    repo = JobSearchRepository(db)
    latest_version = repo.get_latest_resume_version_for_user(user_id=user_id)
    if latest_version:
        latest_resume = repo.get_latest_resume_for_user(user_id=user_id)
        resume_text = latest_resume.resume_text if latest_resume else ""
        return latest_version.id, latest_version.resume_info_json, resume_text

    # Database is empty for this user, fallback to latest_resume.json on disk
    file_context = get_latest_resume_context()
    try:
        db_resume = repo.create_resume(
            user_id=user_id,
            file_path=file_context.get("file_path", "uploads/resume.pdf"),
            resume_text=file_context.get("resume_text", "")
        )
        db_version = repo.create_resume_version(
            resume_id=db_resume.id,
            version=1,
            resume_info_json=file_context.get("resume_information", {})
        )
        return db_version.id, db_version.resume_info_json, db_resume.resume_text
    except Exception as e:
        logger.error(f"Failed to auto-persist disk cached resume to database for user {user_id}: {e}")
        # Default mock fallback values to prevent crashes
        return 1, file_context.get("resume_information", {}), file_context.get("resume_text", "")


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@router.post("/resume-review")
async def get_resume_review(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 1: Analyze the uploaded resume and return overall score, strengths,
    weaknesses, ATS compatibility, suggestions, and suggestions.
    """
    logger.info(f"Resume review request received for user: {current_user.email}")
    version_id, resume_info, resume_text = get_latest_resume_version_context(db, user_id=current_user.id)
    
    try:
        review_result = await review_resume(resume_text, resume_info)
        
        # Persist review report in DB
        from app.repository.db_repository import JobSearchRepository
        repo = JobSearchRepository(db)
        repo.create_resume_review(user_id=current_user.id, resume_version_id=version_id, review_json=review_result)
        
        return review_result
    except Exception as e:
        logger.error(f"Error during resume review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/job-analysis")
async def get_job_analysis(job: JobDetailsSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 2: AI Match Explanation for a target job.
    """
    logger.info(f"Job analysis (Match Explanation) requested for {job.title} at {job.company} by user: {current_user.email}.")
    version_id, resume_info, _ = get_latest_resume_version_context(db, user_id=current_user.id)
    job_details = job.model_dump()
    
    try:
        match_explanation = await analyze_job_match(resume_info, job_details)
        return match_explanation
    except Exception as e:
        logger.error(f"Error during job analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/skill-gap")
async def get_skill_gap(job: JobDetailsSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 3: Skill Gap Analysis endpoint.
    """
    logger.info(f"Skill gap analysis requested for {job.title} at {job.company} by user: {current_user.email}.")
    version_id, resume_info, _ = get_latest_resume_version_context(db, user_id=current_user.id)
    job_details = job.model_dump()
    
    try:
        gap_analysis = await analyze_skill_gap(resume_info, job_details)
        
        # Persist skill gap report in DB
        from app.repository.db_repository import JobSearchRepository
        repo = JobSearchRepository(db)
        repo.create_skill_gap_report(
            user_id=current_user.id,
            resume_version_id=version_id,
            job_title=job.title,
            job_company=job.company,
            gap_json=gap_analysis
        )
        
        return gap_analysis
    except Exception as e:
        logger.error(f"Error during skill gap analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/prepare-interview")
async def get_interview_prep(job: JobDetailsSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 4: Prepare Interview questions.
    """
    logger.info(f"Interview preparation requested for {job.title} at {job.company} by user: {current_user.email}.")
    version_id, resume_info, _ = get_latest_resume_version_context(db, user_id=current_user.id)
    job_details = job.model_dump()
    
    try:
        prep_questions = await prepare_interview(resume_info, job_details)
        return prep_questions
    except Exception as e:
        logger.error(f"Error during interview prep generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/mock-interview/start")
async def start_mock_interview(request: MockInterviewStartRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 5 (Part A): Starts a mock interview.
    Generates 5 questions, creates a session, and returns the first question.
    """
    logger.info(f"Mock interview start requested for {request.title} at {request.company} by user: {current_user.email}.")
    version_id, resume_info, _ = get_latest_resume_version_context(db, user_id=current_user.id)
    job_details = request.model_dump()
    
    try:
        session_data = await start_mock_interview_session(resume_info, job_details)
        
        # Retrieve pre-generated questions list from memory to log in database
        from app.services.llm_service import MOCK_INTERVIEW_SESSIONS
        session_id = session_data.get("session_id")
        questions = []
        if session_id in MOCK_INTERVIEW_SESSIONS:
            questions = MOCK_INTERVIEW_SESSIONS[session_id].get("questions", [])

        # Persist session details in database
        from app.repository.db_repository import JobSearchRepository
        repo = JobSearchRepository(db)
        repo.create_interview_session(
            session_id=session_id,
            user_id=current_user.id,
            resume_version_id=version_id,
            job_title=request.title,
            job_company=request.company,
            job_description=request.description,
            questions_json=questions
        )
        
        return session_data
    except Exception as e:
        logger.error(f"Error starting mock interview session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/mock-interview/answer")
async def submit_answer(request: MockInterviewAnswerRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 5 (Part B): Evaluates the user's answer and advances the interview.
    """
    logger.info(f"Mock interview answer submitted for session {request.session_id} by user: {current_user.email}.")
    
    try:
        # Retrieve the question asked at the current index before submitting the answer
        from app.services.llm_service import MOCK_INTERVIEW_SESSIONS
        question_asked = "Mock Question"
        if request.session_id in MOCK_INTERVIEW_SESSIONS:
            session = MOCK_INTERVIEW_SESSIONS[request.session_id]
            idx = session["current_index"]
            if idx < len(session["questions"]):
                question_asked = session["questions"][idx]

        result = await submit_mock_interview_answer(request.session_id, request.answer)
        
        # Persist individual answer log and evaluation scorecard in database
        from app.repository.db_repository import JobSearchRepository
        repo = JobSearchRepository(db)
        
        evaluation = result.get("evaluation", {})
        score = evaluation.get("overall_score", 0)
        
        repo.create_mock_interview_history(
            session_id=request.session_id,
            question=question_asked,
            answer=request.answer,
            score=score,
            evaluation_json=evaluation
        )
        
        # Update session progression details in database
        repo.update_interview_session_index(request.session_id, result["current_index"])
        
        if result["completed"]:
            repo.complete_interview_session(request.session_id)
            
        return result
    except ValueError as ve:
        logger.warning(f"Validation error in mock interview answer: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error evaluating mock interview answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/career-coach")
async def get_career_coach(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Feature 6: High-level long-term Career Coach dashboard.
    """
    logger.info(f"Career coaching recommendation requested by user: {current_user.email}.")
    version_id, resume_info, _ = get_latest_resume_version_context(db, user_id=current_user.id)
    
    try:
        coaching_details = await provide_career_advice(resume_info)
        
        # Persist career coaching report in DB
        from app.repository.db_repository import JobSearchRepository
        repo = JobSearchRepository(db)
        repo.create_career_report(user_id=current_user.id, resume_version_id=version_id, report_json=coaching_details)
        
        return coaching_details
    except Exception as e:
        logger.error(f"Error in career coach suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
