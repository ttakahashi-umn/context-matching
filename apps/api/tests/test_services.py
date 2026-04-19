from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from talent_interview_profile_poc.application.services.extraction_service import ExtractionService
from talent_interview_profile_poc.application.services.profile_service import ProfileService
from talent_interview_profile_poc.application.services.template_service import TemplateService
from talent_interview_profile_poc.domain.enums import ExtractionStatus
from talent_interview_profile_poc.domain.exceptions import ConflictError, DomainValidationError
from talent_interview_profile_poc.infrastructure.inference.stub_llm_gateway import StubStructuredExtractionGateway
from talent_interview_profile_poc.infrastructure.persistence.database import dispose_engine, get_engine, get_session_factory
from talent_interview_profile_poc.infrastructure.persistence.orm_models import Base, ExtractionRunORM
from talent_interview_profile_poc.infrastructure.persistence.repositories_sqlalchemy import (
    SqlAlchemyExtractionRepository,
    SqlAlchemyInterviewRepository,
    SqlAlchemyProfileRepository,
    SqlAlchemyTalentRepository,
    SqlAlchemyTemplateRepository,
)


@pytest.fixture
def session() -> Session:
    dispose_engine()
    Base.metadata.drop_all(bind=get_engine())
    Base.metadata.create_all(bind=get_engine())
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        dispose_engine()


def test_extraction_conflict_when_running(session: Session) -> None:
    talents = SqlAlchemyTalentRepository(session)
    interviews = SqlAlchemyInterviewRepository(session)
    templates = SqlAlchemyTemplateRepository(session)
    extractions = SqlAlchemyExtractionRepository(session)
    t = talents.create("Bob")
    inv = interviews.create(t.id, "hello world")
    tv = templates.create("v1", "version: '1'\nkey: value")
    session.commit()

    row = ExtractionRunORM(
        interview_session_id=inv.id,
        template_version_id=tv.id,
        status=ExtractionStatus.RUNNING.value,
        input_hash="x",
    )
    session.add(row)
    session.commit()

    svc = ExtractionService(
        session=session,
        interviews=interviews,
        templates=templates,
        extractions=extractions,
        gateway=StubStructuredExtractionGateway(),
    )
    with pytest.raises(ConflictError):
        svc.start(inv.id, tv.id)


def test_profile_merge_rejects_non_completed(session: Session) -> None:
    talents = SqlAlchemyTalentRepository(session)
    interviews = SqlAlchemyInterviewRepository(session)
    extractions = SqlAlchemyExtractionRepository(session)
    profiles = SqlAlchemyProfileRepository(session)
    t = talents.create("Carol")
    inv = interviews.create(t.id, "text")
    tv = SqlAlchemyTemplateRepository(session).create("v1", "version: '1'\na: 1")
    run = extractions.create(inv.id, tv.id, ExtractionStatus.FAILED, "hash")
    session.commit()

    ps = ProfileService(talents, interviews, extractions, profiles)
    with pytest.raises(DomainValidationError):
        ps.merge_from_extraction(t.id, run.id)


def test_template_service_rejects_non_mapping(session: Session) -> None:
    svc = TemplateService(SqlAlchemyTemplateRepository(session))
    with pytest.raises(DomainValidationError):
        svc.validate_yaml_structure("- foo\n- bar\n")
