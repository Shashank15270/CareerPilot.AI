import logging
from typing import List, Dict, Any, Optional

from app.services.job_sources.job_aggregator import JobAggregator

logger = logging.getLogger(__name__)

# Preserve legacy exception classes for full backwards compatibility
class JobFetcherError(Exception):
    """Base exception class for job fetcher service."""
    pass

class JobFetcherTimeoutError(JobFetcherError):
    """Exception raised when the job fetching request times out."""
    pass

class JobFetcherNetworkError(JobFetcherError):
    """Exception raised for network connectivity issues."""
    pass

class JobFetcherResponseError(JobFetcherError):
    """Exception raised when the remote API returns an invalid or unexpected response."""
    pass

# Singleton instance of JobAggregator to share resource
_aggregator = JobAggregator()

async def fetch_jobs(
    query: str = "",
    limit: int = 50,
    location: str = "",
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
    Gateway function fetching normalized and deduplicated jobs from all sources
    (Adzuna, JSearch, Remotive, Wellfound, The Muse).
    """
    logger.info(f"fetch_jobs called with query: '{query}', location: '{location}', limit: {limit}")
    
    # Delegate to modern JobAggregator
    return await _aggregator.aggregate_jobs(
        query=query,
        location=location,
        limit=limit,
        workplace_types=workplace_types,
        experience_levels=experience_levels,
        country=country,
        state=state,
        city=city,
        employment_types=employment_types,
        salary_min=salary_min,
        company_name=company_name,
        skills=skills,
        industry=industry
    )
