from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.models.db_models import (
    User, Resume, ResumeVersion, Recommendation, SavedJob,
    CareerReport, ResumeReview, SkillGapReport, InterviewSession, MockInterviewHistory
)
import app.crud.db_crud as crud

class JobSearchRepository:
    def __init__(self, db: Session):
        self.db = db

    # User operations
    def get_user(self, user_id: int) -> Optional[User]:
        return crud.get_user(self.db, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return crud.get_user_by_email(self.db, email)

    def create_user(self, email: str, name: Optional[str] = None) -> User:
        return crud.create_user(self.db, email, name)

    # Resume operations
    def create_resume(self, user_id: int, file_path: str, resume_text: str) -> Resume:
        return crud.create_resume(self.db, user_id, file_path, resume_text)

    def get_resumes_for_user(self, user_id: int) -> List[Resume]:
        return crud.get_resumes_for_user(self.db, user_id)

    def get_latest_resume_for_user(self, user_id: int) -> Optional[Resume]:
        return crud.get_latest_resume_for_user(self.db, user_id)

    # Resume Version operations
    def create_resume_version(self, resume_id: int, version: int, resume_info_json: dict) -> ResumeVersion:
        return crud.create_resume_version(self.db, resume_id, version, resume_info_json)

    def get_latest_resume_version_for_user(self, user_id: int) -> Optional[ResumeVersion]:
        return crud.get_latest_resume_version_for_user(self.db, user_id)

    # Recommendation operations
    def create_recommendation(self, user_id: int, resume_version_id: int, query: Optional[str], results_json: list) -> Recommendation:
        return crud.create_recommendation(self.db, user_id, resume_version_id, query, results_json)

    def get_recommendations_for_user(self, user_id: int) -> List[Recommendation]:
        return crud.get_recommendations_for_user(self.db, user_id)

    # Saved Job operations
    def get_saved_jobs_for_user(self, user_id: int) -> List[SavedJob]:
        return crud.get_saved_jobs_for_user(self.db, user_id)

    def get_saved_job_by_url_for_user(self, user_id: int, url: str) -> Optional[SavedJob]:
        return crud.get_saved_job_by_url_for_user(self.db, user_id, url)

    def create_saved_job(self, user_id: int, title: str, company: str, location: Optional[str], salary: Optional[str], description: Optional[str], url: Optional[str], source: Optional[str], posted_date: Optional[str], workplace_type: Optional[str], company_logo: Optional[str]) -> SavedJob:
        return crud.create_saved_job(
            self.db, user_id, title, company, location, salary, description, url, source, posted_date, workplace_type, company_logo
        )

    def delete_saved_job(self, user_id: int, job_id: int) -> bool:
        return crud.delete_saved_job(self.db, user_id, job_id)

    # Career Report operations
    def create_career_report(self, user_id: int, resume_version_id: int, report_json: dict) -> CareerReport:
        return crud.create_career_report(self.db, user_id, resume_version_id, report_json)

    def get_career_reports_for_user(self, user_id: int) -> List[CareerReport]:
        return crud.get_career_reports_for_user(self.db, user_id)

    def get_latest_career_report_for_user(self, user_id: int) -> Optional[CareerReport]:
        return crud.get_latest_career_report_for_user(self.db, user_id)

    # Resume Review operations
    def create_resume_review(self, user_id: int, resume_version_id: int, review_json: dict) -> ResumeReview:
        return crud.create_resume_review(self.db, user_id, resume_version_id, review_json)

    def get_resume_reviews_for_user(self, user_id: int) -> List[ResumeReview]:
        return crud.get_resume_reviews_for_user(self.db, user_id)

    def get_latest_resume_review_for_user(self, user_id: int) -> Optional[ResumeReview]:
        return crud.get_latest_resume_review_for_user(self.db, user_id)

    # Skill Gap Report operations
    def create_skill_gap_report(self, user_id: int, resume_version_id: int, job_title: str, job_company: str, gap_json: dict) -> SkillGapReport:
        return crud.create_skill_gap_report(self.db, user_id, resume_version_id, job_title, job_company, gap_json)

    def get_skill_gaps_for_user(self, user_id: int) -> List[SkillGapReport]:
        return crud.get_skill_gaps_for_user(self.db, user_id)

    # Interview Session operations
    def create_interview_session(self, session_id: str, user_id: int, resume_version_id: int, job_title: str, job_company: str, job_description: Optional[str], questions_json: list) -> InterviewSession:
        return crud.create_interview_session(self.db, session_id, user_id, resume_version_id, job_title, job_company, job_description, questions_json)

    def get_interview_session(self, session_id: str) -> Optional[InterviewSession]:
        return crud.get_interview_session(self.db, session_id)

    def update_interview_session_index(self, session_id: str, index: int) -> Optional[InterviewSession]:
        return crud.update_interview_session_index(self.db, session_id, index)

    def complete_interview_session(self, session_id: str) -> Optional[InterviewSession]:
        return crud.complete_interview_session(self.db, session_id)

    def get_interview_sessions_for_user(self, user_id: int) -> List[InterviewSession]:
        return crud.get_interview_sessions_for_user(self.db, user_id)

    # Mock Interview History operations
    def create_mock_interview_history(self, session_id: str, question: str, answer: str, score: int, evaluation_json: dict) -> MockInterviewHistory:
        return crud.create_mock_interview_history(self.db, session_id, question, answer, score, evaluation_json)

    def get_history_for_session(self, session_id: str) -> List[MockInterviewHistory]:
        return crud.get_history_for_session(self.db, session_id)
