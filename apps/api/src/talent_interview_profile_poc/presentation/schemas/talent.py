from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TalentCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)


class TalentPatch(BaseModel):
    """PoC では表示名のみ部分更新（必須フィールド 1 つ）。"""

    display_name: str = Field(min_length=1, max_length=255)


class TalentOut(BaseModel):
    id: UUID
    display_name: str
    created_at: datetime
    latest_profile_json: dict[str, Any] | None = None
