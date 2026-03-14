"""
ScoutAI — Pydantic schemas for Reports
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: int
    result_id: int
    pdf_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
