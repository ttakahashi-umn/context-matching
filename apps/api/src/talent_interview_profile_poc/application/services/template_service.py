from __future__ import annotations

from typing import Any
from uuid import UUID

import yaml

from talent_interview_profile_poc.domain.abstractions.repositories import TemplateRepository
from talent_interview_profile_poc.domain.entities.records import TemplateVersion
from talent_interview_profile_poc.domain.exceptions import DomainValidationError, NotFoundError


def _extract_version_label(parsed: dict[str, Any]) -> str:
    v = parsed.get("version")
    if isinstance(v, str) and v.strip():
        return v.strip()
    return "0.0.0"


def _assert_json_like_mapping(obj: Any, path: str = "$") -> None:
    """テンプレート YAML がマッピング根であり、値が過度に複雑でないことを軽く検査する。"""
    if not isinstance(obj, dict):
        raise DomainValidationError(f"template root must be a mapping at {path}")
    for key, val in obj.items():
        if not isinstance(key, str):
            raise DomainValidationError(f"template keys must be strings at {path}")
        if isinstance(val, dict):
            _assert_json_like_mapping(val, f"{path}.{key}")
        elif isinstance(val, list):
            for i, item in enumerate(val):
                if isinstance(item, dict):
                    _assert_json_like_mapping(item, f"{path}.{key}[{i}]")
                elif not isinstance(item, (str, int, float, bool)) and item is not None:
                    raise DomainValidationError(f"unsupported list item type at {path}.{key}[{i}]")
        elif not isinstance(val, (str, int, float, bool)) and val is not None:
            raise DomainValidationError(f"unsupported value type at {path}.{key}")


class TemplateService:
    def __init__(self, templates: TemplateRepository) -> None:
        self._templates = templates

    def validate_yaml_structure(self, yaml_text: str) -> tuple[dict[str, Any], str]:
        try:
            loaded = yaml.safe_load(yaml_text)
        except yaml.YAMLError as exc:
            raise DomainValidationError(f"invalid yaml: {exc}") from exc
        if loaded is None:
            raise DomainValidationError("yaml must not be empty")
        _assert_json_like_mapping(loaded)
        label = _extract_version_label(loaded)
        return loaded, label

    def register(self, yaml_text: str) -> TemplateVersion:
        _, label = self.validate_yaml_structure(yaml_text)
        return self._templates.create(label, yaml_text)

    def list_all(self) -> list[TemplateVersion]:
        return self._templates.list_all()

    def get(self, template_id: UUID) -> TemplateVersion:
        t = self._templates.get_by_id(template_id)
        if t is None:
            raise NotFoundError("template not found")
        return t
