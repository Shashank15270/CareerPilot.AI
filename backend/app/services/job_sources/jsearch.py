import os
import logging
import httpx
from app.services.job_sources.base_source import BaseJobSource

logger = logging.getLogger(__name__)

class JSearchSource(BaseJobSource):
    async def fetch_jobs(self, query: str = "", location: str = "", limit: int = 50) -> list[dict]:
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        
        if not rapidapi_key:
            logger.warning("RapidAPI Key (RAPIDAPI_KEY) not configured. Skipping JSearch.")
            return []

        url = "https://jsearch.p.rapidapi.com/search"
        
        # Build search query for JSearch.
        # If location is provided, merge it into the query string for optimal JSearch matching.
        search_query = query or "developer"
        if location:
            search_query += f" in {location}"
        else:
            # JSearch performs best when location context is explicit. Focus on India as default context.
            search_query += " in India"

        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        params = {
            "query": search_query,
            "page": "1",
            "num_pages": "1"
        }

        try:
            logger.info(f"Fetching jobs from JSearch API with query '{search_query}'...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("data", [])
                    logger.info(f"JSearch API successfully returned {len(results)} jobs.")
                    # Limit the results returned
                    return results[:limit]
                else:
                    logger.error(f"JSearch API returned status {response.status_code}: {response.text}")
                    return []
                    
        except httpx.TimeoutException:
            logger.warning("Timeout occurred while calling JSearch API.")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error while calling JSearch API: {str(e)}")
            return []
