from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from talent_interview_profile_poc.domain.exceptions import DomainError
from talent_interview_profile_poc.infrastructure.persistence.database import get_session_factory
from talent_interview_profile_poc.infrastructure.persistence.schema import init_db
from talent_interview_profile_poc.presentation.error_handlers import domain_error_handler
from talent_interview_profile_poc.seed import ensure_seed_templates
from talent_interview_profile_poc.presentation.routers import (
    exports,
    extractions,
    interviews,
    profiles,
    talents,
    templates,
)

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    SessionLocal = get_session_factory()
    with SessionLocal() as session:
        try:
            ensure_seed_templates(session)
            session.commit()
        except Exception:
            session.rollback()
            _logger.exception("テンプレートシードに失敗しました（API は起動を続行します）")
    yield


app = FastAPI(
    title="Talent Interview Profile PoC",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(DomainError, domain_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(talents.router)
app.include_router(interviews.router)
app.include_router(templates.router)
app.include_router(extractions.router)
app.include_router(profiles.router)
app.include_router(exports.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
