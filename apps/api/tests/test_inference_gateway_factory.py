from __future__ import annotations

import pytest

from talent_interview_profile_poc.infrastructure.inference.inference_gateway_factory import (
    _resolve_inference_engine,
    build_structured_extraction_gateway,
)
from talent_interview_profile_poc.infrastructure.inference.stub_llm_gateway import (
    StubStructuredExtractionGateway,
)


def test_resolve_engine_stub_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TIP_FORCE_STUB_INFERENCE", raising=False)
    monkeypatch.delenv("TIP_USE_OLLAMA", raising=False)
    monkeypatch.delenv("TIP_USE_MLX", raising=False)
    monkeypatch.setenv("TIP_INFERENCE_ENGINE", "stub")
    assert _resolve_inference_engine() == "stub"


def test_resolve_force_stub_overrides_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIP_INFERENCE_ENGINE", "ollama")
    monkeypatch.setenv("TIP_FORCE_STUB_INFERENCE", "1")
    assert _resolve_inference_engine() == "stub"


def test_resolve_legacy_use_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TIP_FORCE_STUB_INFERENCE", raising=False)
    monkeypatch.delenv("TIP_INFERENCE_ENGINE", raising=False)
    monkeypatch.delenv("TIP_USE_MLX", raising=False)
    monkeypatch.setenv("TIP_USE_OLLAMA", "1")
    assert _resolve_inference_engine() == "ollama"


def test_build_gateway_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TIP_FORCE_STUB_INFERENCE", raising=False)
    monkeypatch.setenv("TIP_INFERENCE_ENGINE", "stub")
    gw = build_structured_extraction_gateway()
    assert isinstance(gw, StubStructuredExtractionGateway)
