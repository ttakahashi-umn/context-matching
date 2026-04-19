from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    yaml_text: str = Field(min_length=1)


class TemplateUpdate(BaseModel):
    """既存テンプレート行の YAML を置き換える（`version` ラベルは他行と重複不可）。"""

    yaml_text: str = Field(min_length=1)


class TemplateRegistered(BaseModel):
    template_version_id: UUID
    semver: str


class TemplateOut(BaseModel):
    id: UUID
    version_label: str
    purpose: str
    yaml_text: str
    created_at: datetime
