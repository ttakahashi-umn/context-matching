from __future__ import annotations

from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class TalentCreate(BaseModel):
    family_name: str = Field(min_length=1, max_length=64)
    given_name: str = Field(min_length=1, max_length=64)
    family_name_kana: str = Field(min_length=1, max_length=128)
    given_name_kana: str = Field(min_length=1, max_length=128)


class TalentPatch(BaseModel):
    """いずれか 1 項目以上を指定して部分更新する。"""

    family_name: str | None = Field(default=None, min_length=1, max_length=64)
    given_name: str | None = Field(default=None, min_length=1, max_length=64)
    family_name_kana: str | None = Field(default=None, min_length=1, max_length=128)
    given_name_kana: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def at_least_one_field(self) -> Self:
        if all(
            v is None
            for v in (self.family_name, self.given_name, self.family_name_kana, self.given_name_kana)
        ):
            raise ValueError("少なくとも 1 つの属性を指定してください")
        return self


class TalentOut(BaseModel):
    id: UUID
    family_name: str
    given_name: str
    family_name_kana: str
    given_name_kana: str
    display_label: str
    created_at: datetime
    latest_profile_json: dict[str, Any] | None = None
