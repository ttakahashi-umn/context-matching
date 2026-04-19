from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from talent_interview_profile_poc.application.services.profile_service import ProfileService
from talent_interview_profile_poc.application.services.talent_service import TalentService
from talent_interview_profile_poc.domain.entities.records import Talent
from talent_interview_profile_poc.presentation.deps import get_profile_service, get_talent_service
from talent_interview_profile_poc.presentation.schemas.profile import ProfileSnapshotOut
from talent_interview_profile_poc.presentation.schemas.talent import TalentCreate, TalentOut, TalentPatch

router = APIRouter(prefix="/talents", tags=["talents"])


def _talent_out(t: Talent, *, latest_profile_json: dict | None = None) -> TalentOut:
    return TalentOut(
        id=t.id,
        family_name=t.family_name,
        given_name=t.given_name,
        family_name_kana=t.family_name_kana,
        given_name_kana=t.given_name_kana,
        display_label=t.display_label,
        created_at=t.created_at,
        latest_profile_json=latest_profile_json,
    )


@router.get("")
def list_talents(
    service: Annotated[TalentService, Depends(get_talent_service)],
) -> list[TalentOut]:
    rows = service.list_all()
    return [_talent_out(t, latest_profile_json=None) for t in rows]


@router.post("", status_code=201)
def create_talent(
    body: TalentCreate,
    service: Annotated[TalentService, Depends(get_talent_service)],
) -> TalentOut:
    t = service.register(
        body.family_name,
        body.given_name,
        body.family_name_kana,
        body.given_name_kana,
    )
    return _talent_out(t, latest_profile_json=None)


@router.get("/{talent_id}/profile/history")
def talent_profile_history(
    talent_id: UUID,
    profiles: Annotated[ProfileService, Depends(get_profile_service)],
) -> list[ProfileSnapshotOut]:
    snaps = profiles.history(talent_id)
    return [
        ProfileSnapshotOut(
            id=s.id,
            talent_id=s.talent_id,
            merged_profile_json=s.merged_profile_json,
            source_extraction_run_id=s.source_extraction_run_id,
            created_at=s.created_at,
        )
        for s in snaps
    ]


@router.get("/{talent_id}")
def get_talent(
    talent_id: UUID,
    talents: Annotated[TalentService, Depends(get_talent_service)],
    profiles: Annotated[ProfileService, Depends(get_profile_service)],
) -> TalentOut:
    t = talents.get(talent_id)
    latest = profiles.latest(talent_id)
    return _talent_out(t, latest_profile_json=latest.merged_profile_json if latest else None)


@router.patch("/{talent_id}")
def patch_talent(
    talent_id: UUID,
    body: TalentPatch,
    service: Annotated[TalentService, Depends(get_talent_service)],
) -> TalentOut:
    t = service.update_partial(talent_id, **body.model_dump(exclude_unset=True))
    return _talent_out(t, latest_profile_json=None)
