import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# Load database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Transform PostgreSQL URL to use pg8000 pure-python driver
if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
    # Replaces postgres:// or postgresql:// with postgresql+pg8000://
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://").replace("postgres://", "postgresql+pg8000://")

# Fallback to local SQLite database if connection string is missing or empty
if not DATABASE_URL:
    db_file = os.path.join(os.path.dirname(__file__), "..", "job_search_assistant.db")
    DATABASE_URL = f"sqlite:///{os.path.abspath(db_file)}"
    logger.warning(f"DATABASE_URL not configured. Falling back to local SQLite database at: {DATABASE_URL}")

# Setup engine arguments depending on DB type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.exception(f"Failed to create database engine for {DATABASE_URL}: {e}")
    # Force emergency fallback to temporary sqlite database to avoid crash
    DATABASE_URL = "sqlite:///emergency_job_search_assistant.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(db):
    """
    Creates tables if they don't exist (primarily for SQLite fallback development)
    and seeds the default user required for session persistence.
    """
    try:
        # Create all tables dynamically
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
        
        # Import User model inside the function to avoid circular imports
        from app.models.db_models import User
        
        # Seed default user (id=1) if it doesn't exist
        default_user = db.query(User).filter(User.id == 1).first()
        if not default_user:
            logger.info("Seeding default user into database...")
            default_user = User(
                id=1,
                email="default@example.com",
                name="Default User"
            )
            db.add(default_user)
            db.commit()
            logger.info("Default user seeded successfully.")
    except Exception as e:
        logger.error(f"Error initializing or seeding database: {e}")
        db.rollback()
