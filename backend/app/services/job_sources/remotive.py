import logging
import httpx
from app.services.job_sources.base_source import BaseJobSource

logger = logging.getLogger(__name__)

class RemotiveSource(BaseJobSource):
    async def fetch_jobs(self, query: str = "", location: str = "", limit: int = 50) -> list[dict]:
        # Remotive is remote-only by design.
        # If user explicitly requests a non-remote onsite search, we could optionally skip it,
        # but to maximize options we will still search and let aggregator filter.
        if location and "remote" not in location.lower() and "anywhere" not in location.lower() and "india" not in location.lower():
            logger.info("Non-remote specific location requested. Skipping Remotive source.")
            return []

        url = "https://remotive.com/api/remote-jobs"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        params = {}
        if query:
            params["search"] = query

        try:
            logger.info(f"Fetching remote jobs from Remotive API (query: '{query}')...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get("jobs", [])
                    logger.info(f"Remotive API returned {len(jobs)} jobs.")
                    return jobs[:limit]
                elif response.status_code == 204:
                    logger.info("Remotive API returned no content (204).")
                    return []
                else:
                    logger.error(f"Remotive API returned status {response.status_code}: {response.text}")
                    return []
                    
        except httpx.TimeoutException:
            logger.warning("Timeout occurred while calling Remotive API.")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error while calling Remotive API: {str(e)}")
            return []
