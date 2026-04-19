from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from talent_interview_profile_poc.application.services.interview_service import InterviewService
from talent_interview_profile_poc.presentation.deps import get_interview_service
from talent_interview_profile_poc.presentation.schemas.interview import InterviewCreate, InterviewCreated, InterviewOut

router = APIRouter(prefix="/talents/{talent_id}/interviews", tags=["interviews"])


@router.post("", status_code=201)
def create_interview(
    talent_id: UUID,
    body: InterviewCreate,
    service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewCreated:
    inv = service.add_interview(talent_id, body.transcript_text)
    return InterviewCreated(interview_session_id=inv.id)


@router.get("")
def list_interviews(
    talent_id: UUID,
    service: Annotated[InterviewService, Depends(get_interview_service)],
) -> list[InterviewOut]:
    rows = service.list_for_talent(talent_id)
    return [
        InterviewOut(
            id=r.id,
            talent_id=r.talent_id,
            transcript_text=r.transcript_text,
            created_at=r.created_at,
        )
        for r in rows
    ]
