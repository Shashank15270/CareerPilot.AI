import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.resume_processor import process_resume
from app.services.job_fetcher import fetch_jobs
from app.services.embedding_service import generate_embedding, generate_embeddings
from app.services.semantic_matcher import rank_jobs
from app.config.india import TIER_ELSEWHERE, COUNTRY_NAME

logger = logging.getLogger(__name__)

# Ranking priority, highest first: skills, then experience, then location.
# These weights are the single place that ordering is expressed — raising
# W_SKILLS relative to the others makes skill fit dominate more strongly.
W_SKILLS = 0.60
W_EXPERIENCE = 0.25
W_LOCATION = 0.15

# Seniority ladder, used to score "close but not exact" experience matches.
EXPERIENCE_LADDER = ["Entry Level", "Mid Level", "Senior Level", "Lead", "Executive"]

# How strongly each region tier counts toward the location component.
LOCATION_TIER_SCORE = {0: 1.0, 1: 0.6, 2: 0.2}


def _skill_score(job: Dict[str, Any], wanted_skills: Optional[List[str]]) -> float:
    """
    0..1 measure of how well a job matches the candidate's skills.

    Blends the semantic resume-to-job similarity with a literal overlap against
    the skills the user asked for. Literal overlap is what a user means by
    "match my skills"; semantic similarity catches equivalent phrasing the
    keyword check would miss.
    """
    similarity = float(job.get("similarity_score") or 0.0)

    if not wanted_skills:
        return similarity

    job_skills = {s.lower() for s in (job.get("required_skills") or [])}
    haystack = f"{job.get('title','')} {job.get('description','')}".lower()

    hits = 0
    for skill in wanted_skills:
        s = skill.lower().strip()
        if not s:
            continue
        if s in job_skills or s in haystack:
            hits += 1

    overlap = hits / len([s for s in wanted_skills if s.strip()])
    return (0.5 * similarity) + (0.5 * overlap)


def _experience_score(job: Dict[str, Any], wanted_level: Optional[str]) -> float:
    """
    0..1 measure of seniority fit. Returns a neutral 1.0 when the user did not
    specify a level, so jobs are not penalised for an unstated preference.
    """
    if not wanted_level:
        return 1.0

    job_level = job.get("experience_level") or ""
    if job_level == wanted_level:
        return 1.0

    if job_level in EXPERIENCE_LADDER and wanted_level in EXPERIENCE_LADDER:
        distance = abs(EXPERIENCE_LADDER.index(job_level) - EXPERIENCE_LADDER.index(wanted_level))
        if distance == 1:
            return 0.5  # one rung away is still worth showing
        return 0.1
    return 0.3


def _location_score(job: Dict[str, Any], region_requested: bool) -> float:
    """0..1 measure of regional fit, neutral when no city/state was requested."""
    if not region_requested:
        return 1.0
    return LOCATION_TIER_SCORE.get(job.get("_region_tier", TIER_ELSEWHERE), 0.2)


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
    
    # 2. Formulate query if empty, fallback to recent role, first skill, or general title
    search_query = query
    if not search_query:
        # Try to use the most recent job title
        exp_list = resume_info.get("experience", [])
        if exp_list and isinstance(exp_list, list) and exp_list[0].get("role"):
            search_query = exp_list[0]["role"]
        else:
            # Try to use the first skill from a flattened list
            resume_skills = resume_info.get("skills", {})
            flat_skills = []
            if isinstance(resume_skills, dict):
                for v in resume_skills.values():
                    if isinstance(v, list):
                        flat_skills.extend(v)
            elif isinstance(resume_skills, list):
                flat_skills = resume_skills
                
            if flat_skills:
                search_query = flat_skills[0]
            else:
                search_query = "Professional"
            
    # 3. Retrieve jobs from aggregator.
    # Over-fetch relative to top_k so region tiering has enough out-of-city
    # candidates to top up with when the requested city is thin.
    # ~30 candidates (3 JSearch pages) is enough to tier and rank against
    # without paying for pages the user will never see.
    fetch_limit = max(30, top_k * 3)

    jobs = await fetch_jobs(
        query=search_query,
        limit=fetch_limit,
        country=COUNTRY_NAME,
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
    if not jobs and search_query != "Professional":
        logger.info("First fetch yielded 0 results, attempting fallback search...")
        jobs = await fetch_jobs(
            query="Professional",
            limit=fetch_limit,
            country=COUNTRY_NAME,
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

    # 5b. Composite ranking. Priority order is skills, then experience, then
    # location: a strong skill match in another city outranks a weak one next
    # door, but among comparable candidates the requested region wins.
    wanted_skills = [s.strip() for s in skills.split(",")] if skills else None
    region_requested = bool(city or state)

    for job in ranked_jobs:
        sk = _skill_score(job, wanted_skills)
        ex = _experience_score(job, experience_level)
        lo = _location_score(job, region_requested)
        job["match_breakdown"] = {
            "skills": round(sk, 4),
            "experience": round(ex, 4),
            "location": round(lo, 4),
        }
        job["match_score"] = round(
            (W_SKILLS * sk) + (W_EXPERIENCE * ex) + (W_LOCATION * lo), 4
        )

    ranked_jobs = sorted(ranked_jobs, key=lambda j: -j["match_score"])

    if ranked_jobs:
        top = ranked_jobs[:top_k]
        in_region = sum(1 for j in top if j.get("_region_tier") == 0)
        logger.info(
            f"Composite ranking (skills {W_SKILLS} / exp {W_EXPERIENCE} / loc {W_LOCATION}): "
            f"top score {top[0]['match_score']}, "
            f"{in_region}/{len(top)} in the requested city."
        )

    # 6. Prepare clean list of dictionaries without heavy NumPy/List embeddings
    recommendations = []
    for job in ranked_jobs[:top_k]:
        job_copy = dict(job)
        job_copy.pop("embedding", None)
        job_copy.pop("_region_tier", None)
        recommendations.append(job_copy)

    # 7. Persist recommendation request in database
    if db is not None and user_id is not None:
        try:
            from app.repository.db_repository import JobSearchRepository
            repo = JobSearchRepository(db)
            # Every upload must be persisted. This used to run only when the
            # user had no resume at all ("if not latest_version"), so the first
            # resume ever uploaded stayed pinned in the database forever and
            # every later AI analysis was performed against that stale copy
            # instead of the file the user just submitted.
            uploaded_path = resume.get("file_path", resume_path)
            existing = repo.get_latest_resume_for_user(user_id=user_id)

            if existing and existing.file_path == uploaded_path:
                # Same physical file re-scanned: add a version rather than a
                # duplicate resume row.
                previous = repo.get_latest_resume_version_for_user(user_id=user_id)
                next_version = (previous.version + 1) if previous else 1
                latest_version = repo.create_resume_version(
                    resume_id=existing.id,
                    version=next_version,
                    resume_info_json=resume_info
                )
                logger.info(
                    f"Stored version {next_version} of existing resume {existing.id} "
                    f"for user {user_id}."
                )
            else:
                db_resume = repo.create_resume(
                    user_id=user_id,
                    file_path=uploaded_path,
                    resume_text=resume_text
                )
                latest_version = repo.create_resume_version(
                    resume_id=db_resume.id,
                    version=1,
                    resume_info_json=resume_info
                )
                logger.info(
                    f"Stored newly uploaded resume {db_resume.id} for user {user_id}."
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
