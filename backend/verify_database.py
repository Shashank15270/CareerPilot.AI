import sys
import os
import uuid
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.database import init_db, SessionLocal
from app.repository.db_repository import JobSearchRepository
from app.models.db_models import User

def test_database_persistence():
    print("--- STARTING DATABASE PERSISTENCE VERIFICATION ---")
    
    # 1. Initialize and Seed Database
    db = SessionLocal()
    try:
        init_db(db)
        repo = JobSearchRepository(db)
        
        # 2. Verify Seed User
        print("\n1. Verifying Default Seed User...")
        user = repo.get_user(1)
        assert user is not None, "Default seed user not found!"
        print(f"Success! Seed User: {user.name} ({user.email})")
        
        # 3. Create Resume and Versions
        print("\n2. Creating Resume and Version history...")
        resume_text = "This is a sample resume text containing Python, React, and SQL."
        resume_info = {
            "name": "Default User",
            "skills": ["Python", "React", "SQL"],
            "experience": [{"company": "ADP", "role": "Analyst"}]
        }
        
        db_resume = repo.create_resume(
            user_id=1,
            file_path="uploads/test_resume.pdf",
            resume_text=resume_text
        )
        assert db_resume.id is not None
        print(f"Success! Created Resume ID: {db_resume.id}")
        
        db_version = repo.create_resume_version(
            resume_id=db_resume.id,
            version=1,
            resume_info_json=resume_info
        )
        assert db_version.id is not None
        print(f"Success! Created Resume Version ID: {db_version.id}")
        
        # 4. Create Recommendation Search History
        print("\n3. Creating Recommendation history log...")
        recommendations = [
            {"title": "Software Developer", "company": "ADP", "similarity_score": 0.85},
            {"title": "Data Analyst", "company": "Google", "similarity_score": 0.72}
        ]
        db_rec = repo.create_recommendation(
            user_id=1,
            resume_version_id=db_version.id,
            query="Python",
            results_json=recommendations
        )
        assert db_rec.id is not None
        print(f"Success! Created Recommendation History ID: {db_rec.id}")
        
        # 5. Create Saved Job Bookmark
        print("\n4. Creating Saved Job Bookmark...")
        db_saved = repo.create_saved_job(
            user_id=1,
            title="Senior AI Engineer",
            company="Lemon.io",
            location="Remote",
            salary="$120k",
            description="Awesome job details...",
            url="https://lemon.io/jobs/senior-ai",
            source="Remotive",
            posted_date="2026-07-16",
            workplace_type="Remote",
            company_logo=""
        )
        assert db_saved.id is not None
        print(f"Success! Bookmarked Job ID: {db_saved.id} - '{db_saved.title}'")
        
        # Verify duplicate save check works
        existing = repo.get_saved_job_by_url_for_user(1, "https://lemon.io/jobs/senior-ai")
        assert existing is not None, "Duplicate check fetch failed!"
        print("Success! URL lookup checked successfully.")
        
        # Delete bookmark
        print("\n5. Testing Saved Job deletion...")
        deleted = repo.delete_saved_job(user_id=1, job_id=db_saved.id)
        assert deleted is True, "Delete saved job operation failed!"
        print("Success! Bookmark unsaved successfully.")
        
        # 6. Create Mock Interview Session
        print("\n6. Creating Mock Interview Session...")
        session_id = str(uuid.uuid4())
        questions = [
            "Tell me about yourself.",
            "Explain Python list comprehension.",
            "What is a REST API?"
        ]
        db_session = repo.create_interview_session(
            session_id=session_id,
            user_id=1,
            resume_version_id=db_version.id,
            job_title="Software Developer",
            job_company="ADP",
            job_description="FastAPI role...",
            questions_json=questions
        )
        assert db_session.id == session_id
        print(f"Success! Created Interview Session ID: {db_session.id}")
        
        # Log answer
        print("Submitting and logging answer...")
        repo.create_mock_interview_history(
            session_id=session_id,
            question=questions[0],
            answer="I am a backend developer...",
            score=82,
            evaluation_json={"communication": {"score": 85}}
        )
        
        # Update session progression
        repo.update_interview_session_index(session_id, 1)
        
        # Verify history logs
        histories = repo.get_history_for_session(session_id)
        assert len(histories) == 1
        assert histories[0].score == 82
        print(f"Success! Logged Mock Interview Answer (Score: {histories[0].score})")
        
        # Clean up mock database records created during test to keep it tidy
        print("\nCleaning up test records from database...")
        db.delete(db_session) # Cascades to histories
        db.delete(db_rec)
        db.delete(db_version)
        db.delete(db_resume)
        db.commit()
        print("Test records cleaned up successfully.")
        
        print("\nALL DATABASE PERSISTENCE VERIFIED SUCCESSFULLY!")
        
    except Exception as e:
        print("\nDatabase verification failed:")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database_persistence()
