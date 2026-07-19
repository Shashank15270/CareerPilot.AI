import asyncio
from pprint import pprint

from app.services.job_fetcher import fetch_jobs


async def main():

    print("Fetching jobs...\n")

    jobs = await fetch_jobs(
        query="",
        limit=5
    )

    print(f"Jobs Found: {len(jobs)}")

    print("\n")

    for index, job in enumerate(jobs, start=1):

        print(f"Job {index}")

        print("-" * 70)

        pprint(job)

        print("\n")


if __name__ == "__main__":
    asyncio.run(main())