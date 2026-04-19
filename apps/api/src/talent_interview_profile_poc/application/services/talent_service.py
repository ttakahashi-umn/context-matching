from __future__ import annotations

from uuid import UUID

from talent_interview_profile_poc.domain.abstractions.repositories import TalentRepository
from talent_interview_profile_poc.domain.entities.records import Talent
from talent_interview_profile_poc.domain.exceptions import NotFoundError


class TalentService:
    def __init__(self, talents: TalentRepository) -> None:
        self._talents = talents

    def register(self, display_name: str) -> Talent:
        return self._talents.create(display_name.strip())

    def list_all(self) -> list[Talent]:
        return self._talents.list_all()

    def get(self, talent_id: UUID) -> Talent:
        t = self._talents.get_by_id(talent_id)
        if t is None:
            raise NotFoundError("talent not found")
        return t

    def update_display_name(self, talent_id: UUID, display_name: str) -> Talent:
        t = self._talents.update_display_name(talent_id, display_name.strip())
        if t is None:
            raise NotFoundError("talent not found")
        return t
