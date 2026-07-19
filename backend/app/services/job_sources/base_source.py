from abc import ABC, abstractmethod

class BaseJobSource(ABC):
    @abstractmethod
    async def fetch_jobs(self, query: str = "", location: str = "", limit: int = 50) -> list[dict]:
        """
        Fetches raw job listings from the specific source provider.

        Args:
            query (str): Search queries/keywords.
            location (str): Target search location.
            limit (int): Maximum number of jobs to fetch.

        Returns:
            list[dict]: A list of raw dictionaries from the provider.
        """
        pass
