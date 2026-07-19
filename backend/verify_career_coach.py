import os
import sys
import json
import asyncio
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

# Load dotenv to read .env
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

async def test_llm_features():
    print("--- VERIFYING GROQ LLM SERVICES ---")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY is not configured in .env.")
        print("Please configure GROQ_API_KEY inside 'backend/.env' to proceed.")
        return
        
    print("GROQ_API_KEY is configured. Running test requests...")
    
    # Import services
    from app.services.llm_service import (
        review_resume,
        analyze_job_match,
        analyze_skill_gap,
        prepare_interview,
        start_mock_interview_session,
        submit_mock_interview_answer,
        provide_career_advice
    )
    
    # Check if latest_resume.json exists
    latest_resume_path = backend_path / "uploads" / "latest_resume.json"
    if not latest_resume_path.exists():
        print("No cached resume found at uploads/latest_resume.json.")
        print("Please upload a resume on the recommendation page first to cache your profile context.")
        return
        
    with open(latest_resume_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
        
    resume_text = resume_data.get("resume_text", "")
    resume_info = resume_data.get("resume_information", {})
    
    # Sample Job details for testing
    job_details = {
        "title": "Senior Python Backend Engineer",
        "company": "TechInnovate Solutions",
        "description": "We are looking for a Senior Python Developer with experience in FastAPI, PostgreSQL, AWS, and building high-performance REST APIs. AI/ML integration experience is a plus.",
        "similarity_score": 0.85
    }
    
    try:
        # Test 1: Resume Review
        print("\n1. Testing resume_review...")
        review = await review_resume(resume_text, resume_info)
        print("Resume Score:", review.get("overall_score"))
        print("Summary:", review.get("resume_summary"))
        print("ATS Compatibility Score:", review.get("ats_compatibility_score"))
        print("Success!")
        
        # Test 2: Job Match
        print("\n2. Testing analyze_job_match...")
        match = await analyze_job_match(resume_info, job_details)
        print("Why Matches:", match.get("why_matches"))
        print("Missing Skills:", match.get("missing_skills"))
        print("Success!")
        
        # Test 3: Skill Gap
        print("\n3. Testing analyze_skill_gap...")
        gap = await analyze_skill_gap(resume_info, job_details)
        print("Current Skills count:", len(gap.get("current_skills", [])))
        print("Missing Skills count:", len(gap.get("missing_skills", [])))
        print("Courses Recommended count:", len(gap.get("recommended_courses", [])))
        print("Success!")
        
        # Test 4: Interview Prep
        print("\n4. Testing prepare_interview...")
        prep = await prepare_interview(resume_info, job_details)
        print("Technical Questions count:", len(prep.get("technical_questions", [])))
        print("Behavioral Questions count:", len(prep.get("behavioral_questions", [])))
        print("Success!")
        
        # Test 5: Mock Interview
        print("\n5. Testing Mock Interview workflow...")
        session = await start_mock_interview_session(resume_info, job_details)
        session_id = session.get("session_id")
        first_q = session.get("question")
        print(f"Mock Session started! Session ID: {session_id}")
        print(f"First Question: '{first_q}'")
        
        # Submit answer to question 1
        print("Submitting answer...")
        answer_resp = await submit_mock_interview_answer(session_id, "I have 5 years of experience developing with Python and FastAPI, focusing on clean architecture.")
        eval_score = answer_resp.get("evaluation", {}).get("overall_score")
        print(f"Evaluation Score: {eval_score}")
        print("Next Question:", answer_resp.get("next_question"))
        print("Success!")
        
        # Test 6: Career Coach
        print("\n6. Testing provide_career_advice...")
        coach = await provide_career_advice(resume_info)
        print("Career Path step 1:", coach.get("career_path", [""])[0])
        print("90-Day Plan elements count:", len(coach.get("ninety_day_improvement_plan", [])))
        print("Success!")
        
        print("\nALL LLM API ENDPOINTS VERIFIED AND WORKING CORRECTLY!")
        
    except Exception as e:
        print("\nAPI call failed during validation:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_features())
