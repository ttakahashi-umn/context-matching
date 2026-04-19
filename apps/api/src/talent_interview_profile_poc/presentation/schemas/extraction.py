from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from talent_interview_profile_poc.domain.enums import ExtractionStatus


class ExtractionStart(BaseModel):
    interview_session_id: UUID
    template_version_id: UUID


class ExtractionStarted(BaseModel):
    extraction_run_id: UUID
    status: ExtractionStatus


class ExtractionRunOut(BaseModel):
    id: UUID
    interview_session_id: UUID
    template_version_id: UUID
    status: ExtractionStatus
    result_json: dict[str, Any] | None
    error_message: str | None
    input_hash: str
    model_id: str | None
    prompt_fingerprint: str | None
    created_at: datetime
