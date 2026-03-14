"""
ScoutAI — Database models and engine setup (SQLAlchemy + SQLite)
"""

import os
import json
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------
# Use PostgreSQL if DATABASE_URL is provided, otherwise fallback to SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Render provides postgres:// but SQLAlchemy requires postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "scoutai.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# For PostgreSQL, we don't need check_same_thread
engine_args = {}
if "sqlite" in DATABASE_URL:
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, **engine_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    """Yield a DB session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    sport = Column(String(60), nullable=False)
    age = Column(Integer, nullable=True)
    region = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    jobs = relationship("AnalysisJob", back_populates="athlete", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="athlete", cascade="all, delete-orphan")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    video_path = Column(String(500), nullable=True)
    image_path = Column(String(500), nullable=True)
    sport = Column(String(60), nullable=False)
    status = Column(
        SAEnum("pending", "processing", "complete", "failed", name="job_status"),
        default="pending",
    )
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    athlete = relationship("Athlete", back_populates="jobs")
    result = relationship("AnalysisResult", back_populates="job", uselist=False, cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False, unique=True)
    talent_score = Column(Float, nullable=True)
    grade = Column(String(30), nullable=True)
    metrics_json = Column(Text, nullable=True)       # JSON string
    breakdown_json = Column(Text, nullable=True)      # JSON string
    ai_summary = Column(Text, nullable=True)
    jersey_number = Column(String(10), nullable=True)
    scoreboard_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    job = relationship("AnalysisJob", back_populates="result")
    report = relationship("Report", back_populates="result", uselist=False, cascade="all, delete-orphan")

    # Helpers to parse JSON fields
    @property
    def metrics(self):
        return json.loads(self.metrics_json) if self.metrics_json else {}

    @property
    def breakdown(self):
        return json.loads(self.breakdown_json) if self.breakdown_json else {}


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False, unique=True)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    result = relationship("AnalysisResult", back_populates="report")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=True)
    role = Column(SAEnum("user", "bot", name="chat_role"), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(60), nullable=True)
    sport = Column(String(60), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    athlete = relationship("Athlete", back_populates="chat_messages")


# ---------------------------------------------------------------------------
# Create tables
# ---------------------------------------------------------------------------

def init_db():
    """Create all tables and seed with benchmark data if empty."""
    Base.metadata.create_all(bind=engine)
    
    # Check if we need to seed (look for specific benchmark name)
    db = SessionLocal()
    try:
        exists = db.query(Athlete).filter(Athlete.name == "Elite Pro A").first()
        if not exists:
            print("[INFO] Seeding database with benchmark athletes...")
            # 1. Create Benchmark Athletes
            benchmarks = [
                {"name": "Elite Pro A", "sport": "Football", "age": 24, "region": "Europe", "score": 92.5, "grade": "Elite"},
                {"name": "Elite Pro B", "sport": "Basketball", "age": 22, "region": "USA", "score": 89.1, "grade": "Elite"},
                {"name": "Rising Star", "sport": "Football", "age": 19, "region": "South America", "score": 84.5, "grade": "Advanced"},
                {"name": "Fast Track", "sport": "Sprint", "age": 21, "region": "Africa", "score": 88.0, "grade": "Elite"},
            ]
            
            for b in benchmarks:
                athlete = Athlete(name=b["name"], sport=b["sport"], age=b["age"], region=b["region"])
                db.add(athlete)
                db.commit()
                db.refresh(athlete)
                
                # Create a completed job for them
                job = AnalysisJob(athlete_id=athlete.id, sport=b["sport"], status="complete", progress=100)
                db.add(job)
                db.commit()
                db.refresh(job)
                
                # Create the result
                result = AnalysisResult(
                    job_id=job.id,
                    talent_score=b["score"],
                    grade=b["grade"],
                    ai_summary=f"Benchmark performance for {b['name']}.",
                    metrics_json=json.dumps({"avg_speed": 28.5, "max_speed": 34.2, "jump_height": 65.0}),
                    breakdown_json=json.dumps({"speed": 95, "athleticism": 90, "technique": 85})
                )
                db.add(result)
            
            db.commit()
            print("[INFO] Seeding complete.")
    finally:
        db.close()
