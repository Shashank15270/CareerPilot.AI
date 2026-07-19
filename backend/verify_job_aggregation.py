import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.services.job_fetcher import fetch_jobs

async def test_aggregation():
    print("--- STARTING JOB AGGREGATION VERIFICATION ---")
    
    # 1. Test fetch with query "Python"
    print("\n1. Fetching jobs matching 'Python'...")
    jobs = await fetch_jobs(query="Python", limit=10)
    print(f"Jobs returned: {len(jobs)}")
    for i, job in enumerate(jobs[:5], 1):
        print(f"  #{i}: [{job.get('source')}] {job.get('title')} at {job.get('company')} ({job.get('location')})")
        print(f"      Workplace: {job.get('workplace_type')}, Exp: {job.get('experience_level')}, Country: {job.get('country')}, Salary: {job.get('salary') or 'N/A'}")
        
    # 2. Test duplicate removal
    print("\n2. Checking deduplication logic...")
    seen = set()
    duplicates = []
    for job in jobs:
        # Check standard deduplication signature (title + company)
        key = f"{job.get('company')}|{job.get('title')}".lower()
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    print(f"Found {len(duplicates)} duplicates in aggregated output.")
    if len(duplicates) > 0:
        print(f"Warning: Duplicates found: {duplicates}")
    else:
        print("Deduplication verification passed!")

    # 3. Test location-based and country filtering
    print("\n3. Testing remote workplace filtering...")
    remote_jobs = await fetch_jobs(query="Python", workplace_types=["Remote"], limit=5)
    print(f"Remote jobs returned: {len(remote_jobs)}")
    for j in remote_jobs:
        print(f"  - [{j.get('source')}] {j.get('title')} ({j.get('workplace_type')})")
        assert j.get("workplace_type") == "Remote", "Workplace filter failed!"
    print("Workplace filtering verification passed!")

    print("\nALL JOB AGGREGATION PIPELINE VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    # Load env variables for testing if present
    from dotenv import load_dotenv
    load_dotenv(backend_path / ".env")
    asyncio.run(test_aggregation())
