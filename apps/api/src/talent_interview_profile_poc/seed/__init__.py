"""起動時シード（テンプレート等）。"""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from talent_interview_profile_poc.application.services.template_service import TemplateService
from talent_interview_profile_poc.infrastructure.persistence.repositories_sqlalchemy import (
    SqlAlchemyTemplateRepository,
)

logger = logging.getLogger(__name__)

# `version` と一致させる（一覧・追跡で識別しやすい）
SEED_IT_ENGINEER_VERSION = "seed-it-engineer-v1"


def ensure_seed_templates(session: Session) -> None:
    """汎用 IT エンジニア面談テンプレが未登録なら 1 件だけ投入する。"""
    repo = SqlAlchemyTemplateRepository(session)
    if any(t.version_label == SEED_IT_ENGINEER_VERSION for t in repo.list_all()):
        return
    yaml_path = Path(__file__).resolve().parent / "it_engineer_interview.yaml"
    if not yaml_path.is_file():
        logger.warning("seed yaml missing: %s", yaml_path)
        return
    yaml_text = yaml_path.read_text(encoding="utf-8")
    TemplateService(repo).register(yaml_text)
