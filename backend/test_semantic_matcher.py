import asyncio

from app.services.job_fetcher import fetch_jobs
from app.services.embedding_service import generate_embedding
from app.services.semantic_matcher import rank_jobs


async def main():

    resume = """
    Python
    FastAPI
    Docker
    Machine Learning
    """

    resume_embedding = generate_embedding(resume)

    jobs = await fetch_jobs(query="python", limit=10)

    for job in jobs:
        job["embedding"] = generate_embedding(job["description"])

    ranked_jobs = rank_jobs(resume_embedding, jobs)

    print("\nTop 5 Jobs:\n")

    for job in ranked_jobs[:5]:
        print(job["title"])
        print(job["company"])
        print(round(job["similarity_score"], 3))
        print()


if __name__ == "__main__":
    asyncio.run(main())