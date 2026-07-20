import os
import logging
import httpx

from app.services.job_sources.base_source import BaseJobSource
from app.config.india import JSEARCH_COUNTRY, COUNTRY_NAME, canonical_city

logger = logging.getLogger(__name__)

# JSearch returns ~10 results per page.
# Measured latency: 1 page ~6.7s, 3 pages ~9.9s, 5 pages ~15.5s. Three pages
# (~29 jobs) is the best return-per-second, and keeps us well clear of the
# request timeout even when the network is slow.
RESULTS_PER_PAGE = 10
MAX_PAGES = 3

# Generous relative to the ~10s worst case above, so ordinary variance does not
# turn a good search into an empty result set.
REQUEST_TIMEOUT_SECONDS = 45.0


class JSearchSource(BaseJobSource):
    async def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 50,
        employment_types: list[str] | None = None,
        workplace_types: list[str] | None = None,
        date_posted: str | None = None,
    ) -> list[dict]:
        rapidapi_key = os.getenv("RAPIDAPI_KEY")

        if not rapidapi_key:
            logger.warning("RapidAPI Key (RAPIDAPI_KEY) not configured. Skipping JSearch.")
            return []

        # JSearch retired the original /search endpoint (it now 404s with
        # "Endpoint '/search' does not exist"); /search-v2 is the current one.
        url = "https://jsearch.p.rapidapi.com/search-v2"

        # Location goes in the query text (JSearch has no separate city param),
        # but the country is sent as a real parameter so results are actually
        # scoped server-side rather than hoped for via the query wording.
        city = canonical_city(location) if location else ""
        search_query = query or "professional"
        if city:
            search_query = f"{search_query} in {city}, {COUNTRY_NAME}"
        else:
            search_query = f"{search_query} in {COUNTRY_NAME}"

        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }

        # Ask for enough pages to cover the requested limit, capped so a large
        # limit cannot burn the whole RapidAPI quota in one search.
        num_pages = min(max(1, -(-limit // RESULTS_PER_PAGE)), MAX_PAGES)

        params = {
            "query": search_query,
            "page": "1",
            "num_pages": str(num_pages),
            "country": JSEARCH_COUNTRY,
        }

        if date_posted:
            params["date_posted"] = date_posted

        # JSearch expects a comma-separated list of its own enum values.
        emp_map = {
            "Full-time": "FULLTIME",
            "Part-time": "PARTTIME",
            "Contract": "CONTRACTOR",
            "Internship": "INTERN",
        }
        if employment_types:
            mapped = [emp_map[t] for t in employment_types if t in emp_map]
            if mapped:
                params["employment_types"] = ",".join(mapped)

        # Only send work_from_home when the user asked exclusively for Remote;
        # sending false would wrongly exclude remote-friendly onsite listings.
        if workplace_types and set(workplace_types) == {"Remote"}:
            params["work_from_home"] = "true"

        try:
            logger.info(
                f"Fetching jobs from JSearch (query='{search_query}', "
                f"country={JSEARCH_COUNTRY}, pages={num_pages})..."
            )
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    # v2 nests the listings under data.jobs (v1 returned a bare
                    # list at data). Tolerate both so a future revert is safe.
                    payload = data.get("data") or {}
                    if isinstance(payload, dict):
                        results = payload.get("jobs") or []
                    else:
                        results = payload
                    logger.info(f"JSearch API successfully returned {len(results)} jobs.")
                    return results[:limit]

                if response.status_code in (401, 403):
                    logger.error(
                        "JSearch rejected the API key (status %s). Check RAPIDAPI_KEY "
                        "and that the JSearch API is subscribed on RapidAPI.",
                        response.status_code,
                    )
                    return []

                if response.status_code == 429:
                    logger.error("JSearch rate limit exceeded (429). Try again later.")
                    return []

                logger.error(f"JSearch API returned status {response.status_code}: {response.text}")
                return []

        except httpx.TimeoutException:
            logger.warning("Timeout occurred while calling JSearch API.")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error while calling JSearch API: {str(e)}")
            return []
