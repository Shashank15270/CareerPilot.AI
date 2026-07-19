import logging
import httpx
from app.services.job_sources.base_source import BaseJobSource

logger = logging.getLogger(__name__)

class TheMuseSource(BaseJobSource):
    async def fetch_jobs(self, query: str = "", location: str = "", limit: int = 50) -> list[dict]:
        url = "https://www.themuse.com/api/public/jobs"
        
        # The Muse expects page parameter (0-indexed)
        params = {
            "page": 0
        }
        
        # Location mapping: if specific location is provided, pass it.
        # Otherwise, default to "India" or "Flexible" to match target focus.
        if location:
            params["location"] = location
        else:
            # Let's search general flexible/remote options or India
            params["location"] = "Flexible / Remote"

        try:
            logger.info(f"Fetching jobs from The Muse API with params: {params}...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    logger.info(f"The Muse API returned {len(results)} jobs.")
                    
                    # Local query filtering: The Muse public API doesn't support a general keyword parameter 'what' or 'q'.
                    # It only supports category, level, location, and company.
                    # Therefore, we filter locally by the query keyword to ensure relevant results.
                    if query:
                        q_lower = query.lower()
                        filtered = []
                        for job in results:
                            # Check title, company name, categories or description content
                            company_name = job.get("company", {}).get("name", "").lower()
                            title = job.get("name", "").lower()
                            desc = job.get("contents", "").lower()
                            
                            if (q_lower in title or 
                                q_lower in company_name or 
                                q_lower in desc):
                                filtered.append(job)
                        
                        logger.info(f"Filtered The Muse results locally: {len(results)} -> {len(filtered)} matching query.")
                        return filtered[:limit]
                        
                    return results[:limit]
                else:
                    logger.error(f"The Muse API returned status {response.status_code}: {response.text}")
                    return []
                    
        except httpx.TimeoutException:
            logger.warning("Timeout occurred while calling The Muse API.")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error while calling The Muse API: {str(e)}")
            return []
