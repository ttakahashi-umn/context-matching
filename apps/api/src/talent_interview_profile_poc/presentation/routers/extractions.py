from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from talent_interview_profile_poc.application.services.extraction_service import ExtractionService
from talent_interview_profile_poc.presentation.deps import get_extraction_service
from talent_interview_profile_poc.presentation.schemas.extraction import (
    ExtractionRunOut,
    ExtractionStart,
    ExtractionStarted,
)

router = APIRouter(prefix="/extractions", tags=["extractions"])


@router.post("", status_code=201)
def start_extraction(
    body: ExtractionStart,
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
) -> ExtractionStarted:
    run = service.start(body.interview_session_id, body.template_version_id)
    return ExtractionStarted(extraction_run_id=run.id, status=run.status)


@router.get("/{run_id}")
def get_extraction(
    run_id: UUID,
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
) -> ExtractionRunOut:
    r = service.get_run(run_id)
    return ExtractionRunOut(
        id=r.id,
        interview_session_id=r.interview_session_id,
        template_version_id=r.template_version_id,
        status=r.status,
        result_json=r.result_json,
        error_message=r.error_message,
        input_hash=r.input_hash,
        model_id=r.model_id,
        prompt_fingerprint=r.prompt_fingerprint,
        created_at=r.created_at,
    )
