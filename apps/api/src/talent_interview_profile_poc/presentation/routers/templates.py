from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from talent_interview_profile_poc.application.services.template_service import TemplateService
from talent_interview_profile_poc.presentation.deps import get_template_service
from talent_interview_profile_poc.presentation.schemas.template import (
    TemplateCreate,
    TemplateOut,
    TemplateRegistered,
    TemplateUpdate,
)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", status_code=201)
def register_template(
    body: TemplateCreate,
    service: Annotated[TemplateService, Depends(get_template_service)],
) -> TemplateRegistered:
    t = service.register(body.yaml_text)
    return TemplateRegistered(template_version_id=t.id, semver=t.version_label)


@router.get("")
def list_templates(
    service: Annotated[TemplateService, Depends(get_template_service)],
) -> list[TemplateOut]:
    rows = service.list_all()
    return [
        TemplateOut(
            id=r.id,
            version_label=r.version_label,
            purpose=r.purpose,
            yaml_text=r.yaml_text,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.get("/{template_id}")
def get_template(
    template_id: UUID,
    service: Annotated[TemplateService, Depends(get_template_service)],
) -> TemplateOut:
    t = service.get(template_id)
    return TemplateOut(
        id=t.id,
        version_label=t.version_label,
        purpose=t.purpose,
        yaml_text=t.yaml_text,
        created_at=t.created_at,
    )


@router.patch("/{template_id}")
def update_template(
    template_id: UUID,
    body: TemplateUpdate,
    service: Annotated[TemplateService, Depends(get_template_service)],
) -> TemplateOut:
    t = service.update(template_id, body.yaml_text)
    return TemplateOut(
        id=t.id,
        version_label=t.version_label,
        purpose=t.purpose,
        yaml_text=t.yaml_text,
        created_at=t.created_at,
    )
