from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InterviewCreate(BaseModel):
    transcript_text: str = Field(min_length=1)


class InterviewCreated(BaseModel):
    interview_session_id: UUID


class InterviewOut(BaseModel):
    id: UUID
    talent_id: UUID
    transcript_text: str
    created_at: datetime
