from __future__ import annotations

import pytest

from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionInput
from talent_interview_profile_poc.infrastructure.inference.prompt_builders import (
    JaFlatJsonPromptBuilder,
    get_prompt_builder,
)


def test_ja_flat_json_builder_shape() -> None:
    b = JaFlatJsonPromptBuilder()
    inp = StructuredExtractionInput(
        transcript_text="hello",
        template_yaml="version: '1'\npurpose: 'p'\nextraction_targets:\n  a: {hint: x}\n",
        template_version_id="tid-1",
    )
    t = b.build(inp)
    assert t.profile_id == "ja_flat_json"
    assert "tid-1" in t.user
    assert "hello" in t.user
    assert len(t.system) > 10


def test_get_prompt_builder_default() -> None:
    b = get_prompt_builder(None)
    assert b.profile_id() == "ja_flat_json"


def test_get_prompt_builder_unknown() -> None:
    with pytest.raises(ValueError, match="unknown prompt profile"):
        get_prompt_builder("no-such-profile")
