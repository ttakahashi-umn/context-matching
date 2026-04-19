from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from talent_interview_profile_poc.domain.entities.records import (
    ExtractionRun,
    InterviewSession,
    ProfileSnapshot,
    Talent,
    TemplateVersion,
)
from talent_interview_profile_poc.domain.enums import ExtractionStatus
from talent_interview_profile_poc.infrastructure.persistence.orm_models import (
    ExtractionRunORM,
    InterviewSessionORM,
    ProfileSnapshotORM,
    TalentORM,
    TemplateVersionORM,
)


def _talent_from_row(row: TalentORM) -> Talent:
    return Talent(
        id=row.id,
        family_name=row.family_name,
        given_name=row.given_name,
        family_name_kana=row.family_name_kana,
        given_name_kana=row.given_name_kana,
        created_at=row.created_at,
    )


def _interview_from_row(row: InterviewSessionORM) -> InterviewSession:
    return InterviewSession(
        id=row.id,
        talent_id=row.talent_id,
        transcript_text=row.transcript_text,
        created_at=row.created_at,
    )


def _template_from_row(row: TemplateVersionORM) -> TemplateVersion:
    return TemplateVersion(
        id=row.id,
        version_label=row.version_label,
        purpose=row.purpose,
        yaml_text=row.yaml_text,
        created_at=row.created_at,
    )


def _extraction_from_row(row: ExtractionRunORM) -> ExtractionRun:
    return ExtractionRun(
        id=row.id,
        interview_session_id=row.interview_session_id,
        template_version_id=row.template_version_id,
        status=ExtractionStatus(row.status),
        result_json=row.result_json,
        error_message=row.error_message,
        input_hash=row.input_hash,
        model_id=row.model_id,
        prompt_fingerprint=row.prompt_fingerprint,
        created_at=row.created_at,
    )


def _snapshot_from_row(row: ProfileSnapshotORM) -> ProfileSnapshot:
    return ProfileSnapshot(
        id=row.id,
        talent_id=row.talent_id,
        merged_profile_json=row.merged_profile_json,
        source_extraction_run_id=row.source_extraction_run_id,
        created_at=row.created_at,
    )


class SqlAlchemyTalentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        family_name: str,
        given_name: str,
        family_name_kana: str,
        given_name_kana: str,
    ) -> Talent:
        row = TalentORM(
            family_name=family_name,
            given_name=given_name,
            family_name_kana=family_name_kana,
            given_name_kana=given_name_kana,
        )
        self._session.add(row)
        self._session.flush()
        return _talent_from_row(row)

    def get_by_id(self, talent_id: UUID) -> Talent | None:
        row = self._session.get(TalentORM, talent_id)
        return _talent_from_row(row) if row else None

    def list_all(self) -> list[Talent]:
        stmt = select(TalentORM).order_by(TalentORM.created_at.desc())
        rows = self._session.scalars(stmt).all()
        return [_talent_from_row(r) for r in rows]

    def update_partial(
        self,
        talent_id: UUID,
        *,
        family_name: str | None = None,
        given_name: str | None = None,
        family_name_kana: str | None = None,
        given_name_kana: str | None = None,
    ) -> Talent | None:
        row = self._session.get(TalentORM, talent_id)
        if row is None:
            return None
        if family_name is not None:
            row.family_name = family_name
        if given_name is not None:
            row.given_name = given_name
        if family_name_kana is not None:
            row.family_name_kana = family_name_kana
        if given_name_kana is not None:
            row.given_name_kana = given_name_kana
        self._session.flush()
        return _talent_from_row(row)


class SqlAlchemyInterviewRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, talent_id: UUID, transcript_text: str) -> InterviewSession:
        row = InterviewSessionORM(talent_id=talent_id, transcript_text=transcript_text)
        self._session.add(row)
        self._session.flush()
        return _interview_from_row(row)

    def get_by_id(self, interview_session_id: UUID) -> InterviewSession | None:
        row = self._session.get(InterviewSessionORM, interview_session_id)
        return _interview_from_row(row) if row else None

    def list_by_talent(self, talent_id: UUID) -> list[InterviewSession]:
        stmt: Select[tuple[InterviewSessionORM]] = (
            select(InterviewSessionORM)
            .where(InterviewSessionORM.talent_id == talent_id)
            .order_by(InterviewSessionORM.created_at.asc())
        )
        rows = self._session.scalars(stmt).all()
        return [_interview_from_row(r) for r in rows]


class SqlAlchemyTemplateRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, version_label: str, purpose: str, yaml_text: str) -> TemplateVersion:
        row = TemplateVersionORM(version_label=version_label, purpose=purpose, yaml_text=yaml_text)
        self._session.add(row)
        self._session.flush()
        return _template_from_row(row)

    def list_all(self) -> list[TemplateVersion]:
        stmt = select(TemplateVersionORM).order_by(TemplateVersionORM.created_at.desc())
        rows = self._session.scalars(stmt).all()
        return [_template_from_row(r) for r in rows]

    def get_by_id(self, template_id: UUID) -> TemplateVersion | None:
        row = self._session.get(TemplateVersionORM, template_id)
        return _template_from_row(row) if row else None


class SqlAlchemyExtractionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def has_running_for_session(self, interview_session_id: UUID) -> bool:
        stmt = select(func.count()).select_from(ExtractionRunORM).where(
            ExtractionRunORM.interview_session_id == interview_session_id,
            ExtractionRunORM.status == ExtractionStatus.RUNNING.value,
        )
        n = self._session.scalar(stmt) or 0
        return int(n) > 0

    def create(
        self,
        interview_session_id: UUID,
        template_version_id: UUID,
        status: ExtractionStatus,
        input_hash: str,
    ) -> ExtractionRun:
        row = ExtractionRunORM(
            interview_session_id=interview_session_id,
            template_version_id=template_version_id,
            status=status.value,
            input_hash=input_hash,
        )
        self._session.add(row)
        self._session.flush()
        return _extraction_from_row(row)

    def update_result(
        self,
        run_id: UUID,
        status: ExtractionStatus,
        result_json: dict | None,
        error_message: str | None,
        model_id: str | None,
        prompt_fingerprint: str | None,
    ) -> ExtractionRun | None:
        row = self._session.get(ExtractionRunORM, run_id)
        if row is None:
            return None
        row.status = status.value
        row.result_json = result_json
        row.error_message = error_message
        row.model_id = model_id
        row.prompt_fingerprint = prompt_fingerprint
        self._session.flush()
        return _extraction_from_row(row)

    def get_by_id(self, run_id: UUID) -> ExtractionRun | None:
        row = self._session.get(ExtractionRunORM, run_id)
        return _extraction_from_row(row) if row else None

    def list_by_interview_session(self, interview_session_id: UUID) -> list[ExtractionRun]:
        stmt = (
            select(ExtractionRunORM)
            .where(ExtractionRunORM.interview_session_id == interview_session_id)
            .order_by(ExtractionRunORM.created_at.asc())
        )
        rows = self._session.scalars(stmt).all()
        return [_extraction_from_row(r) for r in rows]


class SqlAlchemyProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_snapshot(
        self,
        talent_id: UUID,
        merged_profile_json: dict,
        source_extraction_run_id: UUID,
    ) -> ProfileSnapshot:
        row = ProfileSnapshotORM(
            talent_id=talent_id,
            merged_profile_json=merged_profile_json,
            source_extraction_run_id=source_extraction_run_id,
        )
        self._session.add(row)
        self._session.flush()
        return _snapshot_from_row(row)

    def list_snapshots_for_talent(self, talent_id: UUID) -> list[ProfileSnapshot]:
        stmt = (
            select(ProfileSnapshotORM)
            .where(ProfileSnapshotORM.talent_id == talent_id)
            .order_by(ProfileSnapshotORM.created_at.asc())
        )
        rows = self._session.scalars(stmt).all()
        return [_snapshot_from_row(r) for r in rows]

    def get_latest_snapshot(self, talent_id: UUID) -> ProfileSnapshot | None:
        stmt = (
            select(ProfileSnapshotORM)
            .where(ProfileSnapshotORM.talent_id == talent_id)
            .order_by(ProfileSnapshotORM.created_at.desc())
            .limit(1)
        )
        row = self._session.scalars(stmt).first()
        return _snapshot_from_row(row) if row else None
