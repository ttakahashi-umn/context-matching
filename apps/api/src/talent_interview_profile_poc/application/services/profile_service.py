from __future__ import annotations

from typing import Any
from uuid import UUID

from talent_interview_profile_poc.domain.abstractions.repositories import (
    ExtractionRepository,
    InterviewRepository,
    ProfileRepository,
    TalentRepository,
)
from talent_interview_profile_poc.domain.entities.records import ProfileSnapshot
from talent_interview_profile_poc.domain.enums import ExtractionStatus
from talent_interview_profile_poc.domain.exceptions import DomainValidationError, NotFoundError


def _assert_json_safe(obj: Any, path: str = "$") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise DomainValidationError(f"profile json keys must be strings at {path}")
            _assert_json_safe(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _assert_json_safe(item, f"{path}[{i}]")
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return
    else:
        raise DomainValidationError(f"unsupported json value type at {path}")


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


class ProfileService:
    def __init__(
        self,
        talents: TalentRepository,
        interviews: InterviewRepository,
        extractions: ExtractionRepository,
        profiles: ProfileRepository,
    ) -> None:
        self._talents = talents
        self._interviews = interviews
        self._extractions = extractions
        self._profiles = profiles

    def merge_from_extraction(self, talent_id: UUID, extraction_run_id: UUID) -> ProfileSnapshot:
        if self._talents.get_by_id(talent_id) is None:
            raise NotFoundError("talent not found")
        run = self._extractions.get_by_id(extraction_run_id)
        if run is None:
            raise NotFoundError("extraction run not found")
        if run.status != ExtractionStatus.COMPLETED:
            raise DomainValidationError("extraction run is not completed")
        if run.result_json is None:
            raise DomainValidationError("extraction run has no result payload")

        interview = self._interviews.get_by_id(run.interview_session_id)
        if interview is None:
            raise DomainValidationError("interview session missing for extraction run")
        if interview.talent_id != talent_id:
            raise DomainValidationError("extraction run does not belong to the given talent")

        _assert_json_safe(run.result_json)

        latest = self._profiles.get_latest_snapshot(talent_id)
        base: dict[str, Any] = dict(latest.merged_profile_json) if latest else {}
        merged = deep_merge(base, run.result_json)
        _assert_json_safe(merged)
        return self._profiles.create_snapshot(
            talent_id=talent_id,
            merged_profile_json=merged,
            source_extraction_run_id=extraction_run_id,
        )

    def history(self, talent_id: UUID) -> list[ProfileSnapshot]:
        if self._talents.get_by_id(talent_id) is None:
            raise NotFoundError("talent not found")
        return self._profiles.list_snapshots_for_talent(talent_id)

    def latest(self, talent_id: UUID) -> ProfileSnapshot | None:
        if self._talents.get_by_id(talent_id) is None:
            raise NotFoundError("talent not found")
        return self._profiles.get_latest_snapshot(talent_id)
