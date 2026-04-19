from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from talent_interview_profile_poc.application.services.profile_service import ProfileService
from talent_interview_profile_poc.presentation.deps import get_profile_service
from talent_interview_profile_poc.presentation.schemas.profile import ProfileMerge, ProfileSnapshotOut

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/merge", status_code=201)
def merge_profile(
    body: ProfileMerge,
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileSnapshotOut:
    snap = service.merge_from_extraction(body.talent_id, body.extraction_run_id)
    return ProfileSnapshotOut(
        id=snap.id,
        talent_id=snap.talent_id,
        merged_profile_json=snap.merged_profile_json,
        source_extraction_run_id=snap.source_extraction_run_id,
        created_at=snap.created_at,
    )
