import asyncio

from app.services.recommendation_engine import recommend_jobs


RESUME_PATH = "uploads/1f0986e69c1b47628ddbd226b4291dbb.pdf"


async def main():

    print("=" * 100)
    print("AI JOB RECOMMENDATION ENGINE")
    print("=" * 100)

    recommendations = await recommend_jobs(
        resume_path=RESUME_PATH,
        query="",
        top_k=5
    )

    if not recommendations:
        print("\nNo recommendations found.")
        return

    print(f"\nTop {len(recommendations)} Recommended Jobs\n")

    for index, job in enumerate(recommendations, start=1):

        print("=" * 100)
        print(f"Recommendation #{index}")
        print("=" * 100)

        print(f"Title             : {job['title']}")
        print(f"Company           : {job['company']}")
        print(f"Location          : {job['location']}")
        print(f"Employment Type   : {job['employment_type']}")
        print(f"Salary            : {job['salary']}")
        print(f"Similarity Score  : {job['similarity_score']:.4f}")
        print(f"Source            : {job['source']}")
        print(f"URL               : {job['url']}")

        print("\nDescription Preview")
        print("-" * 100)

        description = job["description"]

        if len(description) > 400:
            print(description[:400] + "...")
        else:
            print(description)

        print("\n")


if __name__ == "__main__":
    asyncio.run(main())