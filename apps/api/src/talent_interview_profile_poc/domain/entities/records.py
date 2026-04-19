from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from talent_interview_profile_poc.domain.enums import ExtractionStatus


@dataclass(frozen=True, slots=True)
class Talent:
    id: UUID
    family_name: str
    given_name: str
    family_name_kana: str
    given_name_kana: str
    created_at: datetime

    @property
    def display_label(self) -> str:
        """一覧・エクスポート用の簡易表示（姓 名）。"""
        return f"{self.family_name} {self.given_name}".strip()


@dataclass(frozen=True, slots=True)
class InterviewSession:
    id: UUID
    talent_id: UUID
    transcript_text: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class TemplateVersion:
    id: UUID
    version_label: str
    purpose: str
    yaml_text: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ExtractionRun:
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


@dataclass(frozen=True, slots=True)
class ProfileSnapshot:
    id: UUID
    talent_id: UUID
    merged_profile_json: dict[str, Any]
    source_extraction_run_id: UUID
    created_at: datetime
