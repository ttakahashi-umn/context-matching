from __future__ import annotations

from uuid import UUID

from talent_interview_profile_poc.domain.abstractions.repositories import InterviewRepository, TalentRepository
from talent_interview_profile_poc.domain.entities.records import InterviewSession
from talent_interview_profile_poc.domain.exceptions import DomainValidationError, NotFoundError
from talent_interview_profile_poc.settings import MAX_TRANSCRIPT_BYTES


class InterviewService:
    def __init__(self, talents: TalentRepository, interviews: InterviewRepository) -> None:
        self._talents = talents
        self._interviews = interviews

    def add_interview(self, talent_id: UUID, transcript_text: str) -> InterviewSession:
        if self._talents.get_by_id(talent_id) is None:
            raise NotFoundError("talent not found")
        text = transcript_text
        if not text.strip():
            raise DomainValidationError("transcript_text must not be empty")
        if len(text.encode("utf-8")) > MAX_TRANSCRIPT_BYTES:
            raise DomainValidationError("transcript_text exceeds configured maximum size")
        return self._interviews.create(talent_id, text)

    def list_for_talent(self, talent_id: UUID) -> list[InterviewSession]:
        if self._talents.get_by_id(talent_id) is None:
            raise NotFoundError("talent not found")
        return self._interviews.list_by_talent(talent_id)
