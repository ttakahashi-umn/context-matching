from __future__ import annotations

from typing import Protocol
from uuid import UUID

from talent_interview_profile_poc.domain.entities.records import (
    ExtractionRun,
    InterviewSession,
    ProfileSnapshot,
    Talent,
    TemplateVersion,
)
from talent_interview_profile_poc.domain.enums import ExtractionStatus


class TalentRepository(Protocol):
    def create(
        self,
        family_name: str,
        given_name: str,
        family_name_kana: str,
        given_name_kana: str,
    ) -> Talent: ...
    def get_by_id(self, talent_id: UUID) -> Talent | None: ...
    def list_all(self) -> list[Talent]: ...
    def update_partial(
        self,
        talent_id: UUID,
        *,
        family_name: str | None = None,
        given_name: str | None = None,
        family_name_kana: str | None = None,
        given_name_kana: str | None = None,
    ) -> Talent | None: ...


class InterviewRepository(Protocol):
    def create(self, talent_id: UUID, transcript_text: str) -> InterviewSession: ...
    def get_by_id(self, interview_session_id: UUID) -> InterviewSession | None: ...
    def list_by_talent(self, talent_id: UUID) -> list[InterviewSession]: ...


class TemplateRepository(Protocol):
    def create(self, version_label: str, purpose: str, yaml_text: str) -> TemplateVersion: ...
    def list_all(self) -> list[TemplateVersion]: ...
    def get_by_id(self, template_id: UUID) -> TemplateVersion | None: ...


class ExtractionRepository(Protocol):
    def has_running_for_session(self, interview_session_id: UUID) -> bool: ...
    def list_by_interview_session(self, interview_session_id: UUID) -> list[ExtractionRun]: ...
    def create(
        self,
        interview_session_id: UUID,
        template_version_id: UUID,
        status: ExtractionStatus,
        input_hash: str,
    ) -> ExtractionRun: ...
    def update_result(
        self,
        run_id: UUID,
        status: ExtractionStatus,
        result_json: dict | None,
        error_message: str | None,
        model_id: str | None,
        prompt_fingerprint: str | None,
    ) -> ExtractionRun | None: ...
    def get_by_id(self, run_id: UUID) -> ExtractionRun | None: ...


class ProfileRepository(Protocol):
    def create_snapshot(
        self,
        talent_id: UUID,
        merged_profile_json: dict,
        source_extraction_run_id: UUID,
    ) -> ProfileSnapshot: ...
    def list_snapshots_for_talent(self, talent_id: UUID) -> list[ProfileSnapshot]: ...
    def get_latest_snapshot(self, talent_id: UUID) -> ProfileSnapshot | None: ...
