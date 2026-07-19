from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

# Configuration class update for Pydantic V2 compatibility
class DBBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(DBBaseModel):
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserSchema(UserBase):
    id: int
    created_at: datetime

# Resume Schemas
class ResumeBase(DBBaseModel):
    file_path: str
    resume_text: str

class ResumeCreate(ResumeBase):
    user_id: int

class ResumeSchema(ResumeBase):
    id: int
    user_id: int
    created_at: datetime

# Resume Version Schemas
class ResumeVersionBase(DBBaseModel):
    version: int
    resume_info_json: Dict[str, Any]

class ResumeVersionCreate(ResumeVersionBase):
    resume_id: int

class ResumeVersionSchema(ResumeVersionBase):
    id: int
    resume_id: int
    created_at: datetime

# Recommendation Schemas
class RecommendationBase(DBBaseModel):
    query: Optional[str] = None
    results_json: List[Dict[str, Any]]

class RecommendationCreate(RecommendationBase):
    user_id: int
    resume_version_id: int

class RecommendationSchema(RecommendationBase):
    id: int
    user_id: int
    resume_version_id: int
    created_at: datetime

# Saved Job Schemas
class SavedJobBase(DBBaseModel):
    title: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    posted_date: Optional[str] = None
    workplace_type: Optional[str] = None
    company_logo: Optional[str] = None

class SavedJobCreate(SavedJobBase):
    user_id: int

class SavedJobSchema(SavedJobBase):
    id: int
    user_id: int
    created_at: datetime

# Career Report Schemas
class CareerReportBase(DBBaseModel):
    report_json: Dict[str, Any]

class CareerReportCreate(CareerReportBase):
    user_id: int
    resume_version_id: int

class CareerReportSchema(CareerReportBase):
    id: int
    user_id: int
    resume_version_id: int
    created_at: datetime

# Resume Review Schemas
class ResumeReviewBase(DBBaseModel):
    review_json: Dict[str, Any]

class ResumeReviewCreate(ResumeReviewBase):
    user_id: int
    resume_version_id: int

class ResumeReviewSchema(ResumeReviewBase):
    id: int
    user_id: int
    resume_version_id: int
    created_at: datetime

# Skill Gap Report Schemas
class SkillGapReportBase(DBBaseModel):
    job_title: str
    job_company: str
    gap_json: Dict[str, Any]

class SkillGapReportCreate(SkillGapReportBase):
    user_id: int
    resume_version_id: int

class SkillGapReportSchema(SkillGapReportBase):
    id: int
    user_id: int
    resume_version_id: int
    created_at: datetime

# Mock Interview History Schemas
class MockInterviewHistoryBase(DBBaseModel):
    question: str
    answer: str
    score: int
    evaluation_json: Dict[str, Any]

class MockInterviewHistoryCreate(MockInterviewHistoryBase):
    session_id: str

class MockInterviewHistorySchema(MockInterviewHistoryBase):
    id: int
    session_id: str
    created_at: datetime

# Interview Session Schemas
class InterviewSessionBase(DBBaseModel):
    job_title: str
    job_company: str
    job_description: Optional[str] = None
    questions_json: List[str]
    current_index: int
    completed: bool

class InterviewSessionCreate(InterviewSessionBase):
    id: str # UUID
    user_id: int
    resume_version_id: int

class InterviewSessionSchema(InterviewSessionBase):
    id: str
    user_id: int
    resume_version_id: int
    created_at: datetime
    history: List[MockInterviewHistorySchema] = []
