from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileMerge(BaseModel):
    talent_id: UUID
    extraction_run_id: UUID


class ProfileSnapshotOut(BaseModel):
    id: UUID
    talent_id: UUID
    merged_profile_json: dict[str, Any]
    source_extraction_run_id: UUID
    created_at: datetime
