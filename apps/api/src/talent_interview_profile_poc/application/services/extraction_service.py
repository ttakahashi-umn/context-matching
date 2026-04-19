from __future__ import annotations

import hashlib
from uuid import UUID

from sqlalchemy.orm import Session

from talent_interview_profile_poc.domain.abstractions.inference import (
    StructuredExtractionGateway,
    StructuredExtractionInput,
)
from talent_interview_profile_poc.domain.abstractions.repositories import (
    ExtractionRepository,
    InterviewRepository,
    TemplateRepository,
)
from talent_interview_profile_poc.domain.entities.records import ExtractionRun
from talent_interview_profile_poc.domain.enums import ExtractionStatus
from talent_interview_profile_poc.domain.exceptions import (
    ConflictError,
    InferenceError,
    NotFoundError,
)


def compute_input_hash(transcript: str, template_yaml: str, template_version_id: UUID) -> str:
    raw = f"{transcript}\n{template_yaml}\n{template_version_id}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class ExtractionService:
    def __init__(
        self,
        session: Session,
        interviews: InterviewRepository,
        templates: TemplateRepository,
        extractions: ExtractionRepository,
        gateway: StructuredExtractionGateway,
    ) -> None:
        self._session = session
        self._interviews = interviews
        self._templates = templates
        self._extractions = extractions
        self._gateway = gateway

    def start(self, interview_session_id: UUID, template_version_id: UUID) -> ExtractionRun:
        interview = self._interviews.get_by_id(interview_session_id)
        if interview is None:
            raise NotFoundError("interview session not found")
        template = self._templates.get_by_id(template_version_id)
        if template is None:
            raise NotFoundError("template version not found")

        if self._extractions.has_running_for_session(interview_session_id):
            raise ConflictError("extraction already running for this interview session")

        input_hash = compute_input_hash(
            interview.transcript_text, template.yaml_text, template_version_id
        )
        run = self._extractions.create(
            interview_session_id=interview_session_id,
            template_version_id=template_version_id,
            status=ExtractionStatus.RUNNING,
            input_hash=input_hash,
        )
        self._session.commit()

        inp = StructuredExtractionInput(
            transcript_text=interview.transcript_text,
            template_yaml=template.yaml_text,
            template_version_id=str(template_version_id),
        )
        try:
            out = self._gateway.infer(inp)
        except Exception as exc:
            self._extractions.update_result(
                run.id,
                ExtractionStatus.FAILED,
                result_json=None,
                error_message=str(exc),
                model_id=None,
                prompt_fingerprint=None,
            )
            self._session.commit()
            raise InferenceError("structured extraction failed") from exc

        updated = self._extractions.update_result(
            run.id,
            ExtractionStatus.COMPLETED,
            result_json=out.data,
            error_message=None,
            model_id=out.model_id,
            prompt_fingerprint=out.prompt_fingerprint,
        )
        self._session.commit()
        if updated is None:
            raise InferenceError("failed to persist extraction result")
        return updated

    def get_run(self, run_id: UUID) -> ExtractionRun:
        run = self._extractions.get_by_id(run_id)
        if run is None:
            raise NotFoundError("extraction run not found")
        return run
