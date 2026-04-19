from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionInput
from talent_interview_profile_poc.infrastructure.inference.ollama_llm_gateway import (
    OllamaStructuredExtractionGateway,
    _parse_json_object,
)


def test_parse_json_object_plain() -> None:
    assert _parse_json_object('  {"a": 1} ') == {"a": 1}


def test_parse_json_object_fenced() -> None:
    text = 'Here:\n```json\n{"x": "y"}\n```\n'
    assert _parse_json_object(text) == {"x": "y"}


def test_ollama_gateway_infer_success() -> None:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"message": {"content": '{"summary": "ok", "template_version_id": "tid"}'}}

    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_client
    mock_cm.__exit__.return_value = None

    inp = StructuredExtractionInput(
        transcript_text="hello",
        template_yaml="version: '1'\npurpose: 'p'\n",
        template_version_id="tid",
    )

    with patch("talent_interview_profile_poc.infrastructure.inference.ollama_llm_gateway.httpx.Client") as Cls:
        Cls.return_value = mock_cm
        gw = OllamaStructuredExtractionGateway(base_url="http://ollama.test", model="m1", timeout_sec=5.0)
        out = gw.infer(inp)

    assert out.data["summary"] == "ok"
    assert out.model_id == "ollama:m1"
    assert len(out.prompt_fingerprint) == 16
    mock_client.post.assert_called_once()
    args, kwargs = mock_client.post.call_args
    assert args[0] == "http://ollama.test/api/chat"
    assert kwargs["json"]["model"] == "m1"
    assert kwargs["json"]["format"] == "json"
    assert kwargs["json"]["messages"][0]["role"] == "system"
    assert kwargs["json"]["messages"][1]["role"] == "user"
    assert "options" in kwargs["json"]
    assert "temperature" in kwargs["json"]["options"]


def test_ollama_gateway_dict_content() -> None:
    """一部の応答で content がすでに dict になる場合。"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"message": {"content": {"k": 1}}}

    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_client
    mock_cm.__exit__.return_value = None

    inp = StructuredExtractionInput(transcript_text="t", template_yaml="a: 1", template_version_id="id")

    with patch("talent_interview_profile_poc.infrastructure.inference.ollama_llm_gateway.httpx.Client") as Cls:
        Cls.return_value = mock_cm
        gw = OllamaStructuredExtractionGateway(base_url="http://x", model="m", timeout_sec=1.0)
        out = gw.infer(inp)
    assert out.data == {"k": 1}


def test_parse_json_object_invalid() -> None:
    with pytest.raises(ValueError):
        _parse_json_object("not json")


def test_ollama_gateway_model_missing_404() -> None:
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = ""
    mock_resp.json.return_value = {"error": "model 'm1' not found"}

    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_client
    mock_cm.__exit__.return_value = None

    inp = StructuredExtractionInput(transcript_text="t", template_yaml="a: 1", template_version_id="id")

    with patch("talent_interview_profile_poc.infrastructure.inference.ollama_llm_gateway.httpx.Client") as Cls:
        Cls.return_value = mock_cm
        gw = OllamaStructuredExtractionGateway(base_url="http://x", model="m1", timeout_sec=1.0)
        with pytest.raises(RuntimeError, match=r"ollama HTTP 404.*model 'm1' not found"):
            gw.infer(inp)
