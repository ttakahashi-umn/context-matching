from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from talent_interview_profile_poc.application.services.export_service import ExportService
from talent_interview_profile_poc.application.services.extraction_service import ExtractionService
from talent_interview_profile_poc.application.services.interview_service import InterviewService
from talent_interview_profile_poc.application.services.profile_service import ProfileService
from talent_interview_profile_poc.application.services.talent_service import TalentService
from talent_interview_profile_poc.application.services.template_service import TemplateService
from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionGateway
from talent_interview_profile_poc.infrastructure.inference.inference_gateway_factory import (
    build_structured_extraction_gateway,
)
from talent_interview_profile_poc.infrastructure.persistence.database import get_session_factory
from talent_interview_profile_poc.infrastructure.persistence.repositories_sqlalchemy import (
    SqlAlchemyExtractionRepository,
    SqlAlchemyInterviewRepository,
    SqlAlchemyProfileRepository,
    SqlAlchemyTalentRepository,
    SqlAlchemyTemplateRepository,
)

_gateway: StructuredExtractionGateway | None = None


def get_inference_gateway() -> StructuredExtractionGateway:
    global _gateway
    if _gateway is None:
        _gateway = build_structured_extraction_gateway()
    return _gateway


def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_talent_service(session: DbSession) -> TalentService:
    return TalentService(SqlAlchemyTalentRepository(session))


def get_interview_service(session: DbSession) -> InterviewService:
    return InterviewService(
        SqlAlchemyTalentRepository(session),
        SqlAlchemyInterviewRepository(session),
    )


def get_template_service(session: DbSession) -> TemplateService:
    return TemplateService(SqlAlchemyTemplateRepository(session))


def get_profile_service(session: DbSession) -> ProfileService:
    return ProfileService(
        SqlAlchemyTalentRepository(session),
        SqlAlchemyInterviewRepository(session),
        SqlAlchemyExtractionRepository(session),
        SqlAlchemyProfileRepository(session),
    )


def get_extraction_service(
    session: DbSession, gateway: Annotated[StructuredExtractionGateway, Depends(get_inference_gateway)]
) -> ExtractionService:
    return ExtractionService(
        session=session,
        interviews=SqlAlchemyInterviewRepository(session),
        templates=SqlAlchemyTemplateRepository(session),
        extractions=SqlAlchemyExtractionRepository(session),
        gateway=gateway,
    )


def get_export_service(session: DbSession) -> ExportService:
    return ExportService(
        SqlAlchemyTalentRepository(session),
        SqlAlchemyInterviewRepository(session),
        SqlAlchemyExtractionRepository(session),
        SqlAlchemyProfileRepository(session),
    )
