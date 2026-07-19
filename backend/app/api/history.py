import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user_optional
from app.models.db_models import User
from app.repository.db_repository import JobSearchRepository
from app.schemas.db_schemas import SavedJobBase, SavedJobSchema, RecommendationSchema, InterviewSessionSchema, CareerReportSchema, MockInterviewHistorySchema

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/saved-jobs", response_model=List[SavedJobSchema])
@router.get("/history/saved-jobs", response_model=List[SavedJobSchema])
def get_saved_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves all jobs saved/bookmarked by the candidate.
    """
    logger.info(f"Retrieving saved jobs for user: {current_user.email}")
    repo = JobSearchRepository(db)
    return repo.get_saved_jobs_for_user(current_user.id)

@router.post("/saved-jobs", response_model=SavedJobSchema)
def save_job(job: SavedJobBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Bookmarks/saves a target job description.
    """
    logger.info(f"User {current_user.email} saving job: {job.title} at {job.company}")
    repo = JobSearchRepository(db)
    if job.url:
        existing = repo.get_saved_job_by_url_for_user(current_user.id, job.url)
        if existing:
            return existing
    return repo.create_saved_job(
        user_id=current_user.id,
        title=job.title,
        company=job.company,
        location=job.location,
        salary=job.salary,
        description=job.description,
        url=job.url,
        source=job.source,
        posted_date=job.posted_date,
        workplace_type=job.workplace_type,
        company_logo=job.company_logo
    )

@router.delete("/saved-jobs/{job_id}")
def unsave_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Removes a bookmarked job.
    """
    logger.info(f"User {current_user.email} unsaving job ID: {job_id}")
    repo = JobSearchRepository(db)
    success = repo.delete_saved_job(current_user.id, job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found or not owned by user."
        )
    return {"message": "Job unsaved successfully."}

@router.get("/history/resumes")
def get_resume_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves history logs of candidate's uploaded resumes and version parses.
    """
    logger.info(f"Retrieving resume logs for user: {current_user.email}")
    repo = JobSearchRepository(db)
    resumes = repo.get_resumes_for_user(current_user.id)
    
    results = []
    for r in resumes:
        for v in r.versions:
            results.append({
                "id": r.id,
                "version_id": v.id,
                "file_path": r.file_path,
                "version": v.version,
                "created_at": v.created_at,
                "resume_info": v.resume_info_json
            })
    
    # If no versions exist, just return basic resume details
    if not results:
        for r in resumes:
            results.append({
                "id": r.id,
                "version_id": None,
                "file_path": r.file_path,
                "version": None,
                "created_at": r.created_at,
                "resume_info": {}
            })
            
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results

@router.get("/history/recommendations", response_model=List[RecommendationSchema])
def get_recommendation_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves previous job recommendation search records.
    """
    logger.info(f"Retrieving recommendation search logs for user: {current_user.email}")
    repo = JobSearchRepository(db)
    return repo.get_recommendations_for_user(current_user.id)

@router.get("/history/interviews", response_model=List[InterviewSessionSchema])
def get_interview_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves history of started mock interview sessions.
    """
    logger.info(f"Retrieving mock interview sessions for user: {current_user.email}")
    repo = JobSearchRepository(db)
    return repo.get_interview_sessions_for_user(current_user.id)

@router.get("/history/interviews/{session_id}", response_model=List[MockInterviewHistorySchema])
def get_interview_history_details(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves answer-by-answer score evaluation details for a specific interview session.
    """
    logger.info(f"Retrieving interview scorecard details for session: {session_id}")
    repo = JobSearchRepository(db)
    session = repo.get_interview_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock interview session not found or unauthorized."
        )
    return repo.get_history_for_session(session_id)

@router.get("/history/career-coach", response_model=List[CareerReportSchema])
def get_career_coach_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves previous career coaching dashboard reports.
    """
    logger.info(f"Retrieving career reports history logs for user: {current_user.email}")
    repo = JobSearchRepository(db)
    return repo.get_career_reports_for_user(current_user.id)
