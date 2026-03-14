"""
ScoutAI — Pydantic schemas for Athletes and Analysis results
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Athlete schemas
# ---------------------------------------------------------------------------

class AthleteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    sport: str = Field(..., min_length=1, max_length=60)
    age: Optional[int] = Field(None, ge=5, le=100)
    region: Optional[str] = Field(None, max_length=120)


class AthleteResponse(BaseModel):
    id: int
    name: str
    sport: str
    age: Optional[int] = None
    region: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Analysis schemas
# ---------------------------------------------------------------------------

class AnalysisJobResponse(BaseModel):
    id: int
    athlete_id: int
    sport: str
    status: str
    progress: int
    video_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsBreakdown(BaseModel):
    speed: float = 0
    athleticism: float = 0
    technique: float = 0
    agility: float = 0
    consistency: float = 0


class ResultResponse(BaseModel):
    id: int
    job_id: int
    talent_score: Optional[float] = None
    grade: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    breakdown: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None
    jersey_number: Optional[str] = None
    scoreboard_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    athlete_id: int
    name: str
    sport: str
    age: Optional[int] = None
    region: Optional[str] = None
    talent_score: float
    grade: str


# ---------------------------------------------------------------------------
# Upload schemas
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    message: str
    job_id: Optional[int] = None
    file_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Chatbot schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    sport: Optional[str] = None
    athlete_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    category: Optional[str] = None
    suggestions: List[str] = []


class ChatHistoryEntry(BaseModel):
    id: int
    role: str
    message: str
    category: Optional[str] = None
    sport: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
