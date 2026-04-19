from __future__ import annotations

from uuid import UUID

from talent_interview_profile_poc.domain.abstractions.repositories import TalentRepository
from talent_interview_profile_poc.domain.entities.records import Talent
from talent_interview_profile_poc.domain.exceptions import DomainValidationError, NotFoundError


class TalentService:
    def __init__(self, talents: TalentRepository) -> None:
        self._talents = talents

    def register(
        self,
        family_name: str,
        given_name: str,
        family_name_kana: str,
        given_name_kana: str,
    ) -> Talent:
        fn, gn, fk, gk = (
            family_name.strip(),
            given_name.strip(),
            family_name_kana.strip(),
            given_name_kana.strip(),
        )
        if not fn or not gn or not fk or not gk:
            raise DomainValidationError("姓・名・読み仮名（姓・名）はいずれも空にできません")
        return self._talents.create(fn, gn, fk, gk)

    def list_all(self) -> list[Talent]:
        return self._talents.list_all()

    def get(self, talent_id: UUID) -> Talent:
        t = self._talents.get_by_id(talent_id)
        if t is None:
            raise NotFoundError("talent not found")
        return t

    def update_partial(
        self,
        talent_id: UUID,
        *,
        family_name: str | None = None,
        given_name: str | None = None,
        family_name_kana: str | None = None,
        given_name_kana: str | None = None,
    ) -> Talent:
        kwargs: dict[str, str] = {}
        for key, val in (
            ("family_name", family_name),
            ("given_name", given_name),
            ("family_name_kana", family_name_kana),
            ("given_name_kana", given_name_kana),
        ):
            if val is not None:
                s = val.strip()
                if not s:
                    raise DomainValidationError(f"{key} は空にできません")
                kwargs[key] = s
        if not kwargs:
            raise DomainValidationError("更新する項目がありません")
        t = self._talents.update_partial(talent_id, **kwargs)
        if t is None:
            raise NotFoundError("talent not found")
        return t
