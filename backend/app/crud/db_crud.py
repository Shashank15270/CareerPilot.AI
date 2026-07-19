from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from app.models.db_models import (
    User, Resume, ResumeVersion, Recommendation, SavedJob,
    CareerReport, ResumeReview, SkillGapReport, InterviewSession, MockInterviewHistory
)

# User operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, name: Optional[str] = None) -> User:
    db_user = User(email=email, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Resume operations
def create_resume(db: Session, user_id: int, file_path: str, resume_text: str) -> Resume:
    db_resume = Resume(user_id=user_id, file_path=file_path, resume_text=resume_text)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def get_resumes_for_user(db: Session, user_id: int) -> List[Resume]:
    return db.query(Resume).filter(Resume.user_id == user_id).order_by(desc(Resume.created_at)).all()

def get_latest_resume_for_user(db: Session, user_id: int) -> Optional[Resume]:
    return db.query(Resume).filter(Resume.user_id == user_id).order_by(desc(Resume.created_at)).first()

# Resume Version operations
def create_resume_version(db: Session, resume_id: int, version: int, resume_info_json: dict) -> ResumeVersion:
    db_version = ResumeVersion(resume_id=resume_id, version=version, resume_info_json=resume_info_json)
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

def get_latest_resume_version_for_user(db: Session, user_id: int) -> Optional[ResumeVersion]:
    latest_resume = get_latest_resume_for_user(db, user_id)
    if not latest_resume:
        return None
    return db.query(ResumeVersion).filter(ResumeVersion.resume_id == latest_resume.id).order_by(desc(ResumeVersion.version)).first()

# Recommendation operations
def create_recommendation(db: Session, user_id: int, resume_version_id: int, query: Optional[str], results_json: list) -> Recommendation:
    db_rec = Recommendation(user_id=user_id, resume_version_id=resume_version_id, query=query, results_json=results_json)
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

def get_recommendations_for_user(db: Session, user_id: int) -> List[Recommendation]:
    return db.query(Recommendation).filter(Recommendation.user_id == user_id).order_by(desc(Recommendation.created_at)).all()

# Saved Job operations
def get_saved_jobs_for_user(db: Session, user_id: int) -> List[SavedJob]:
    return db.query(SavedJob).filter(SavedJob.user_id == user_id).order_by(desc(SavedJob.created_at)).all()

def get_saved_job_by_url_for_user(db: Session, user_id: int, url: str) -> Optional[SavedJob]:
    return db.query(SavedJob).filter(SavedJob.user_id == user_id, SavedJob.url == url).first()

def create_saved_job(db: Session, user_id: int, title: str, company: str, location: Optional[str], salary: Optional[str], description: Optional[str], url: Optional[str], source: Optional[str], posted_date: Optional[str], workplace_type: Optional[str], company_logo: Optional[str]) -> SavedJob:
    db_job = SavedJob(
        user_id=user_id, title=title, company=company, location=location, salary=salary,
        description=description, url=url, source=source, posted_date=posted_date,
        workplace_type=workplace_type, company_logo=company_logo
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def delete_saved_job(db: Session, user_id: int, job_id: int) -> bool:
    db_job = db.query(SavedJob).filter(SavedJob.user_id == user_id, SavedJob.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
        return True
    return False

# Career Report operations
def create_career_report(db: Session, user_id: int, resume_version_id: int, report_json: dict) -> CareerReport:
    db_report = CareerReport(user_id=user_id, resume_version_id=resume_version_id, report_json=report_json)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_career_reports_for_user(db: Session, user_id: int) -> List[CareerReport]:
    return db.query(CareerReport).filter(CareerReport.user_id == user_id).order_by(desc(CareerReport.created_at)).all()

def get_latest_career_report_for_user(db: Session, user_id: int) -> Optional[CareerReport]:
    return db.query(CareerReport).filter(CareerReport.user_id == user_id).order_by(desc(CareerReport.created_at)).first()

# Resume Review operations
def create_resume_review(db: Session, user_id: int, resume_version_id: int, review_json: dict) -> ResumeReview:
    db_review = ResumeReview(user_id=user_id, resume_version_id=resume_version_id, review_json=review_json)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_resume_reviews_for_user(db: Session, user_id: int) -> List[ResumeReview]:
    return db.query(ResumeReview).filter(ResumeReview.user_id == user_id).order_by(desc(ResumeReview.created_at)).all()

def get_latest_resume_review_for_user(db: Session, user_id: int) -> Optional[ResumeReview]:
    return db.query(ResumeReview).filter(ResumeReview.user_id == user_id).order_by(desc(ResumeReview.created_at)).first()

# Skill Gap Report operations
def create_skill_gap_report(db: Session, user_id: int, resume_version_id: int, job_title: str, job_company: str, gap_json: dict) -> SkillGapReport:
    db_report = SkillGapReport(
        user_id=user_id, resume_version_id=resume_version_id,
        job_title=job_title, job_company=job_company, gap_json=gap_json
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_skill_gaps_for_user(db: Session, user_id: int) -> List[SkillGapReport]:
    return db.query(SkillGapReport).filter(SkillGapReport.user_id == user_id).order_by(desc(SkillGapReport.created_at)).all()

# Interview Session operations
def create_interview_session(db: Session, session_id: str, user_id: int, resume_version_id: int, job_title: str, job_company: str, job_description: Optional[str], questions_json: list) -> InterviewSession:
    db_session = InterviewSession(
        id=session_id, user_id=user_id, resume_version_id=resume_version_id,
        job_title=job_title, job_company=job_company, job_description=job_description,
        questions_json=questions_json, current_index=0, completed=False
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_interview_session(db: Session, session_id: str) -> Optional[InterviewSession]:
    return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()

def update_interview_session_index(db: Session, session_id: str, index: int) -> Optional[InterviewSession]:
    db_session = get_interview_session(db, session_id)
    if db_session:
        db_session.current_index = index
        db.commit()
        db.refresh(db_session)
    return db_session

def complete_interview_session(db: Session, session_id: str) -> Optional[InterviewSession]:
    db_session = get_interview_session(db, session_id)
    if db_session:
        db_session.completed = True
        db.commit()
        db.refresh(db_session)
    return db_session

def get_interview_sessions_for_user(db: Session, user_id: int) -> List[InterviewSession]:
    return db.query(InterviewSession).filter(InterviewSession.user_id == user_id).order_by(desc(InterviewSession.created_at)).all()

# Mock Interview History operations
def create_mock_interview_history(db: Session, session_id: str, question: str, answer: str, score: int, evaluation_json: dict) -> MockInterviewHistory:
    db_history = MockInterviewHistory(
        session_id=session_id, question=question, answer=answer, score=score, evaluation_json=evaluation_json
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_history_for_session(db: Session, session_id: str) -> List[MockInterviewHistory]:
    return db.query(MockInterviewHistory).filter(MockInterviewHistory.session_id == session_id).order_by(MockInterviewHistory.created_at).all()
