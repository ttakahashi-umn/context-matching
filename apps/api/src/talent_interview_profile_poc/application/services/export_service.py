from __future__ import annotations

from typing import Any
from uuid import UUID

from talent_interview_profile_poc.domain.abstractions.repositories import (
    ExtractionRepository,
    InterviewRepository,
    ProfileRepository,
    TalentRepository,
)
from talent_interview_profile_poc.domain.exceptions import NotFoundError


class ExportService:
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

    def build_talent_export(self, talent_id: UUID) -> dict[str, Any]:
        talent = self._talents.get_by_id(talent_id)
        if talent is None:
            raise NotFoundError("talent not found")

        interviews = self._interviews.list_by_talent(talent_id)
        interview_payload: list[dict[str, Any]] = []
        for inv in interviews:
            runs = self._extractions.list_by_interview_session(inv.id)
            interview_payload.append(
                {
                    "interview_session_id": str(inv.id),
                    "created_at": inv.created_at.isoformat(),
                    "transcript_text": inv.transcript_text,
                    "extraction_runs": [
                        {
                            "extraction_run_id": str(r.id),
                            "template_version_id": str(r.template_version_id),
                            "status": r.status.value,
                            "input_hash": r.input_hash,
                            "model_id": r.model_id,
                            "prompt_fingerprint": r.prompt_fingerprint,
                            "created_at": r.created_at.isoformat(),
                        }
                        for r in runs
                    ],
                }
            )

        snapshots = self._profiles.list_snapshots_for_talent(talent_id)
        snapshot_payload = [
            {
                "profile_snapshot_id": str(s.id),
                "merged_profile_json": s.merged_profile_json,
                "source_extraction_run_id": str(s.source_extraction_run_id),
                "created_at": s.created_at.isoformat(),
            }
            for s in snapshots
        ]

        return {
            "talent": {
                "id": str(talent.id),
                "display_name": talent.display_name,
                "created_at": talent.created_at.isoformat(),
            },
            "interviews": interview_payload,
            "profile_snapshots": snapshot_payload,
        }
