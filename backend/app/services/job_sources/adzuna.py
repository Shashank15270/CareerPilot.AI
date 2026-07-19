import os
import logging
import httpx
from app.services.job_sources.base_source import BaseJobSource

logger = logging.getLogger(__name__)

class AdzunaSource(BaseJobSource):
    async def fetch_jobs(self, query: str = "", location: str = "", limit: int = 50) -> list[dict]:
        app_id = os.getenv("ADZUNA_APP_ID")
        app_key = os.getenv("ADZUNA_APP_KEY")

        if not app_id or not app_key:
            logger.warning("Adzuna API credentials (ADZUNA_APP_ID or ADZUNA_APP_KEY) not set. Skipping Adzuna.")
            return []

        # Determine country. If location or query indicates another market, we map it,
        # but focus heavily on the Indian market ('in').
        country = "in"
        loc_lower = location.lower()
        
        # Simple mapping for major international markets
        if "united states" in loc_lower or "usa" in loc_lower or " u.s." in loc_lower or " us " in loc_lower:
            country = "us"
        elif "united kingdom" in loc_lower or "uk" in loc_lower or " u.k." in loc_lower:
            country = "gb"
        elif "canada" in loc_lower:
            country = "ca"
        elif "australia" in loc_lower:
            country = "au"
        elif "germany" in loc_lower:
            country = "de"
        elif "france" in loc_lower:
            country = "fr"

        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": min(limit, 50),
            "content-type": "application/json"
        }
        
        if query:
            params["what"] = query
        if location:
            params["where"] = location

        try:
            logger.info(f"Fetching jobs from Adzuna API for country '{country}', query '{query}', location '{location}'...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    logger.info(f"Adzuna API successfully returned {len(results)} jobs.")
                    return results
                else:
                    logger.error(f"Adzuna API returned status {response.status_code}: {response.text}")
                    return []
                    
        except httpx.TimeoutException:
            logger.warning("Timeout occurred while calling Adzuna API.")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error while calling Adzuna API: {str(e)}")
            return []
