import asyncio
import logging
import re
from typing import List, Dict, Any, Optional

from app.services.job_sources.jsearch import JSearchSource
from app.services.job_sources.job_normalizer import normalize_job
from app.config.india import (
    COUNTRY_NAME,
    CITY_ALIASES,
    TIER_EXACT_CITY,
    TIER_SAME_STATE,
    TIER_ELSEWHERE,
    canonical_city,
    state_for_city,
    looks_indian,
)

logger = logging.getLogger(__name__)

def _normalize_string(text: str) -> str:
    """Helper to clean string by lowering, removing punctuation, and stripping whitespace."""
    if not text:
        return ""
    # Lowercase, remove non-alphanumeric, collapse spaces
    cleaned = text.lower()
    cleaned = re.sub(r'[^a-z0-9\s]', '', cleaned)
    return " ".join(cleaned.split())

def _clean_company_name(company: str) -> str:
    """Strips legal entity suffixes from company name for deduplication matching."""
    name = _normalize_string(company)
    suffixes = [
        "llc", "inc", "pvt", "ltd", "private", "limited", "corp", "corporation", 
        "gmbh", "co", "solutions", "technologies", "technology", "systems"
    ]
    words = name.split()
    filtered_words = [w for w in words if w not in suffixes]
    return "".join(filtered_words) if filtered_words else name

def _are_locations_similar(loc1: str, loc2: str) -> bool:
    """Determines if two location strings refer to overlapping or identical spaces."""
    l1 = _normalize_string(loc1)
    l2 = _normalize_string(loc2)
    
    if not l1 or not l2:
        return False

    # If one contains the other, or they share a major word (other than common fillers)
    words1 = set(l1.split())
    words2 = set(l2.split())
    
    common_fillers = {"in", "and", "the", "of", "remote", "hybrid", "onsite", "anywhere", "worldwide"}
    w1_filtered = words1 - common_fillers
    w2_filtered = words2 - common_fillers
    
    if not w1_filtered or not w2_filtered:
        return True
        
    # If there is intersection between location keywords
    return len(w1_filtered.intersection(w2_filtered)) > 0

def _calculate_job_quality(job: dict) -> int:
    """Grades job quality: higher score means longer description, populated salary/logo/skills."""
    score = 0
    if job.get("description"):
        score += len(job["description"]) # Points for detailed description
    if job.get("salary"):
        score += 200 # Higher weight for publishing salaries
    if job.get("company_logo"):
        score += 50
    if job.get("required_skills"):
        score += len(job["required_skills"]) * 10
    return score

def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detects and filters out duplicate job listings, retaining the highest quality copy.
    Deduplicates based on Company Name, Job Title, and Location similarity.
    """
    unique_jobs: Dict[str, Dict[str, Any]] = {}
    
    for job in jobs:
        comp_key = _clean_company_name(job.get("company") or "")
        title_key = _normalize_string(job.get("title") or "")
        
        # Create a compound key base. Since location comparison uses words,
        # we will check existing matches for the comp_key + title_key base.
        base_key = f"{comp_key}|{title_key}"
        
        # Check if we already have a candidate matching company and title
        duplicate_found = False
        for existing_key in list(unique_jobs.keys()):
            if existing_key.startswith(base_key):
                existing_job = unique_jobs[existing_key]
                if _are_locations_similar(job.get("location") or "", existing_job.get("location") or ""):
                    duplicate_found = True
                    # Compare qualities and retain the better one
                    if _calculate_job_quality(job) > _calculate_job_quality(existing_job):
                        unique_jobs[existing_key] = job
                    break
                    
        if not duplicate_found:
            # Create a unique compound key
            loc_key = _normalize_string(job.get("location") or "anywhere")
            unique_key = f"{base_key}|{loc_key}"
            unique_jobs[unique_key] = job
            
    logger.info(f"Deduplication completed: {len(jobs)} total -> {len(unique_jobs)} unique listings.")
    return list(unique_jobs.values())

def _assign_region_tier(job: Dict[str, Any], city: str, state: str) -> int:
    """
    Grades how well a job matches the requested region.
    """
    job_loc = (job.get("location") or "").lower()

    if city:
        target = canonical_city(city)
        if target and target.lower() in job_loc:
            return TIER_EXACT_CITY
        # Match the alias the board actually published, e.g. "Bangalore".
        for variant, canonical in CITY_ALIASES.items():
            if canonical == target and variant in job_loc:
                return TIER_EXACT_CITY

    target_state = state or (state_for_city(city) if city else "")
    if target_state and target_state.lower() in job_loc:
        return TIER_SAME_STATE

    return TIER_ELSEWHERE


class JobAggregator:
    def __init__(self):
        # India-only scope: JSearch is the single active source.
        self.sources = {
            "JSearch": JSearchSource(),
        }

    async def aggregate_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 50,
        workplace_types: Optional[List[str]] = None,
        experience_levels: Optional[List[str]] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        employment_types: Optional[List[str]] = None,
        salary_min: Optional[int] = None,
        company_name: Optional[str] = None,
        skills: Optional[List[str]] = None,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries all sources concurrently, normalizes, deduplicates, and returns unified list.
        """
        target_city = canonical_city(city) if city else ""
        if not location:
            location = target_city

        # Single source now, so it gets the whole budget rather than limit // 2.
        source_limit = max(limit, 20)

        tasks = []
        source_names = list(self.sources.keys())

        for name, source in self.sources.items():
            tasks.append(
                self._safe_fetch(
                    name, source, query, location, source_limit,
                    employment_types=employment_types,
                    workplace_types=workplace_types,
                )
            )

        # Run concurrent calls
        results = await asyncio.gather(*tasks)

        # Merge all raw lists, normalizing them as they enter
        all_normalized_jobs = []
        for name, raw_list in zip(source_names, results):
            for raw_job in raw_list:
                try:
                    normalized = normalize_job(name, raw_job)
                    if normalized:
                        all_normalized_jobs.append(normalized)
                except Exception as exc:
                    logger.error(f"Failed to normalize raw job from {name}: {exc}")

        # Keep only India jobs
        india_jobs = [
            j for j in all_normalized_jobs
            if looks_indian(j.get("location") or "", j.get("country") or "")
        ]
        dropped = len(all_normalized_jobs) - len(india_jobs)
        if dropped:
            logger.info(f"Dropped {dropped} non-India listings ({COUNTRY_NAME}-only scope).")

        # Remove duplicates
        deduplicated = deduplicate_jobs(india_jobs)

        # Apply post-aggregation filters.
        filtered_jobs = self._apply_filters(
            deduplicated,
            workplace_types=workplace_types,
            experience_levels=experience_levels,
            employment_types=employment_types,
            salary_min=salary_min,
            company_name=company_name,
            skills=skills,
            industry=industry
        )

        # Annotate each job with how well it matches the requested region.
        for job in filtered_jobs:
            job["_region_tier"] = _assign_region_tier(job, target_city, state or "")

        exact = sum(1 for j in filtered_jobs if j["_region_tier"] == TIER_EXACT_CITY)
        same_state = sum(1 for j in filtered_jobs if j["_region_tier"] == TIER_SAME_STATE)
        logger.info(
            f"Final aggregated count: {len(filtered_jobs)} jobs "
            f"({exact} exact-city, {same_state} same-state, "
            f"{len(filtered_jobs) - exact - same_state} elsewhere in India)."
        )

        # Return the full tiered pool.
        return filtered_jobs

    async def _safe_fetch(
        self,
        name: str,
        source: Any,
        query: str,
        location: str,
        limit: int,
        employment_types: Optional[List[str]] = None,
        workplace_types: Optional[List[str]] = None,
    ) -> list:
        """Executes source fetch inside a try-catch block to prevent crashing the aggregator."""
        try:
            return await source.fetch_jobs(
                query=query,
                location=location,
                limit=limit,
                employment_types=employment_types,
                workplace_types=workplace_types,
            )
        except TypeError:
            # Source predates the extended signature; fall back to the basics.
            return await source.fetch_jobs(query=query, location=location, limit=limit)
        except Exception as e:
            logger.exception(f"Error fetching jobs from source '{name}': {str(e)}")
            return []

    def _apply_filters(
        self,
        jobs: List[Dict[str, Any]],
        workplace_types: Optional[List[str]] = None,
        experience_levels: Optional[List[str]] = None,
        employment_types: Optional[List[str]] = None,
        salary_min: Optional[int] = None,
        company_name: Optional[str] = None,
        skills: Optional[List[str]] = None,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filters the unified job list by attributes.
        """
        filtered = []
        for job in jobs:
            # 1. Workplace Type Filter (Remote / Hybrid / Onsite)
            if workplace_types:
                if job.get("workplace_type") not in workplace_types:
                    continue
                    
            # 2. Experience Level Filter (Entry Level / Mid Level / Senior Level / Lead / Executive)
            if experience_levels:
                canonical = {"Entry Level", "Mid Level", "Senior Level", "Lead", "Executive"}
                mapped_levels = []
                for exp_in in experience_levels:
                    if exp_in in canonical:
                        mapped_levels.append(exp_in)
                        continue
                    low = exp_in.lower()
                    if 'entry' in low or 'junior' in low or '0' in exp_in:
                        mapped_levels.append('Entry Level')
                    elif 'mid' in low:
                        mapped_levels.append('Mid Level')
                    elif 'senior' in low or 'sr' in low:
                        mapped_levels.append('Senior Level')
                    elif 'lead' in low or 'principal' in low:
                        mapped_levels.append('Lead')
                    elif 'exec' in low or 'director' in low:
                        mapped_levels.append('Executive')

                if mapped_levels and job.get("experience_level") not in mapped_levels:
                    continue

            # 3. Employment Type Filter
            if employment_types:
                if job.get("employment_type") not in employment_types:
                    continue

            # 7. Salary Min Filter
            if salary_min is not None:
                sal_str = job.get("salary") or ""
                # Find all integer digit groups in the formatted string, collapse them
                nums = re.findall(r'\d+', sal_str.replace(',', ''))
                if nums:
                    try:
                        job_sal = int(nums[0])
                        # If it's India lakhs format e.g. 15, let's normalize to full digits
                        if job_sal < 100:
                            job_sal = job_sal * 100000
                        if job_sal < salary_min:
                            continue
                    except ValueError:
                        pass

            # 8. Company Name Filter
            if company_name:
                job_company = job.get("company") or ""
                if company_name.lower() not in job_company.lower():
                    continue

            # 9. Skills Filter
            if skills:
                job_skills_lower = [s.lower() for s in (job.get("required_skills") or [])]
                job_desc_lower = (job.get("description") or "").lower()
                job_title_lower = (job.get("title") or "").lower()
                
                match_any = False
                for sk in skills:
                    sk_l = sk.lower()
                    if sk_l in job_skills_lower or sk_l in job_desc_lower or sk_l in job_title_lower:
                        match_any = True
                        break
                if not match_any:
                    continue

            # 10. Industry Filter
            if industry:
                job_desc_lower = (job.get("description") or "").lower()
                job_title_lower = (job.get("title") or "").lower()
                if industry.lower() not in job_desc_lower and industry.lower() not in job_title_lower:
                    continue

            filtered.append(job)
        return filtered
