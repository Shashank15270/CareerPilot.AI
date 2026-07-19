import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.resume_processor import process_resume
from app.services.job_fetcher import fetch_jobs
from app.services.embedding_service import generate_embedding, generate_embeddings
from app.services.semantic_matcher import rank_jobs

logger = logging.getLogger(__name__)

async def recommend_jobs(
    resume_path: str,
    query: str = "",
    top_k: int = 10,
    db: Optional[Session] = None,
    user_id: Optional[int] = None,
    country: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    experience_level: Optional[str] = None,
    employment_type: Optional[str] = None,
    workplace_type: Optional[str] = None,
    salary_min: Optional[int] = None,
    company_name: Optional[str] = None,
    skills: Optional[str] = None,
    industry: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Given a resume path, queries the job sources aggregator, ranks results using 
    semantic embeddings and cosine similarity, and optionally persists the search in database history.
    """
    logger.info(f"recommend_jobs triggered with resume: '{resume_path}', query: '{query}'")
    
    # 1. Parse and extract resume text and structured info
    resume = process_resume(resume_path)
    resume_text = resume.get("resume_text", "")
    resume_info = resume.get("resume_information", {})
    
    # 2. Formulate query if empty, fallback to first skill, preferred role, or general title
    search_query = query
    if not search_query:
        skills_list = resume_info.get("skills", [])
        if skills_list and isinstance(skills_list, list):
            search_query = skills_list[0]
        else:
            search_query = "Software Engineer"
            
    # 3. Retrieve jobs from aggregator
    jobs = await fetch_jobs(
        query=search_query,
        limit=50,
        country=country,
        state=state,
        city=city,
        experience_levels=[experience_level] if experience_level else None,
        employment_types=[employment_type] if employment_type else None,
        workplace_types=[workplace_type] if workplace_type else None,
        salary_min=salary_min,
        company_name=company_name,
        skills=[s.strip() for s in skills.split(",")] if skills else None,
        industry=industry
    )
    if not jobs and search_query != "Software Engineer":
        logger.info("First fetch yielded 0 results, attempting fallback search...")
        jobs = await fetch_jobs(
            query="Software Engineer",
            limit=50,
            country=country,
            state=state,
            city=city,
            experience_levels=[experience_level] if experience_level else None,
            employment_types=[employment_type] if employment_type else None,
            workplace_types=[workplace_type] if workplace_type else None,
            salary_min=salary_min,
            company_name=company_name,
            skills=[s.strip() for s in skills.split(",")] if skills else None,
            industry=industry
        )
        
    if not jobs:
        logger.warning("No jobs found for search query and fallbacks.")
        return []
        
    # 4. Construct embedding representations for resume and jobs
    parts = []
    if resume_info.get("summary"):
        parts.append(str(resume_info["summary"]))
    if resume_info.get("skills"):
        skills_val = resume_info["skills"]
        parts.append(", ".join(skills_val) if isinstance(skills_val, list) else str(skills_val))
    if resume_info.get("projects") and isinstance(resume_info["projects"], list):
        for proj in resume_info["projects"]:
            if isinstance(proj, dict) and proj.get("description"):
                parts.append(proj["description"])
    if resume_info.get("experience") and isinstance(resume_info["experience"], list):
        for exp in resume_info["experience"]:
            if isinstance(exp, dict) and exp.get("description"):
                parts.append(exp["description"])
                
    resume_embedding_text = "\n".join(parts).strip()
    if not resume_embedding_text:
        resume_embedding_text = resume_text or "Software Engineer Resume"
        
    # Generate resume embedding vector
    resume_embedding = generate_embedding(resume_embedding_text)
    
    # Build text representations for jobs and get embeddings in batch
    job_texts = []
    valid_jobs = []
    for job in jobs:
        req_skills = job.get("required_skills") or []
        skills_str = ", ".join(req_skills) if isinstance(req_skills, list) else str(req_skills)
        text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')} {skills_str}".strip()
        if text:
            job_texts.append(text)
            valid_jobs.append(job)
            
    if not valid_jobs:
        return []
        
    job_embeddings = generate_embeddings(job_texts)
    for job, emb in zip(valid_jobs, job_embeddings):
        # We mutate a copy of the job list to ensure safety
        job["embedding"] = emb
        
    # 5. Rank jobs using scikit-learn cosine similarity
    ranked_jobs = rank_jobs(resume_embedding, valid_jobs)
    
    # 6. Prepare clean list of dictionaries without heavy NumPy/List embeddings
    recommendations = []
    for job in ranked_jobs[:top_k]:
        job_copy = dict(job)
        job_copy.pop("embedding", None)
        recommendations.append(job_copy)
        
    # 7. Persist recommendation request in database
    if db is not None and user_id is not None:
        try:
            from app.repository.db_repository import JobSearchRepository
            repo = JobSearchRepository(db)
            latest_version = repo.get_latest_resume_version_for_user(user_id=user_id)
            if not latest_version:
                logger.info(f"Seeding resume & version metadata in database for user {user_id}...")
                db_resume = repo.create_resume(
                    user_id=user_id,
                    file_path=resume.get("file_path", resume_path),
                    resume_text=resume_text
                )
                latest_version = repo.create_resume_version(
                    resume_id=db_resume.id,
                    version=1,
                    resume_info_json=resume_info
                )
                
            repo.create_recommendation(
                user_id=user_id,
                resume_version_id=latest_version.id,
                query=query,
                results_json=recommendations
            )
            logger.info("Recommendation query results successfully saved to history.")
        except Exception as db_err:
            logger.error(f"Failed to persist recommendations to database history log: {db_err}")
            
    return recommendations
