from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, SessionLocal
from app.api.upload import router as upload_router
from app.api.recommendation import router as recommendation_router
from app.api.career_coach import router as career_coach_router
from app.api.history import router as history_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="AI Job Recommendation Platform",
    description="A production-style backend system for matching job seekers with relevant job postings using AI-driven matching algorithms.",
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()


# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://careerpilott.netlify.app", "https://careerpilotsky.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Register Routers
# -----------------------------
app.include_router(
    upload_router,
    prefix="/api",
    tags=["Resume"],
)

app.include_router(
    recommendation_router,
    prefix="/api",
    tags=["Recommendation"],
)

app.include_router(
    career_coach_router,
    prefix="/api",
    tags=["Career Coach"],
)

app.include_router(
    history_router,
    prefix="/api",
    tags=["History"],
)

app.include_router(
    auth_router,
    prefix="/api",
    tags=["Authentication"],
)


@app.get("/")
async def root():
    return {
        "status": "running",
        "project": "AI Job Recommendation Platform",
        "version": "1.0.0",
    }