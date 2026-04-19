"""ローカル Ollama（HTTP）経由の構造化抽出ゲートウェイ。"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from typing import Any

import httpx

from talent_interview_profile_poc.domain.abstractions.extraction_prompting import (
    StructuredExtractionPromptBuilder,
)
from talent_interview_profile_poc.domain.abstractions.inference import (
    StructuredExtractionGateway,
    StructuredExtractionInput,
    StructuredExtractionOutput,
)
from talent_interview_profile_poc.infrastructure.inference.prompt_builders import get_prompt_builder

logger = logging.getLogger(__name__)


def _ollama_http_error_message(res: httpx.Response) -> str:
    """Ollama が返す JSON の `error` や本文を短く取り出す。"""
    try:
        data = res.json()
        if isinstance(data, dict):
            err = data.get("error")
            if isinstance(err, str) and err.strip():
                return err.strip()
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    text = (res.text or "").strip()
    return text[:800] if text else "(empty body)"


def _parse_json_object(text: str) -> dict[str, Any]:
    """モデル応答から JSON オブジェクトを取り出す（素の JSON または ```json フェンス）。"""
    raw = text.strip()
    if not raw:
        raise ValueError("empty model response")
    try:
        out = json.loads(raw)
        if isinstance(out, dict):
            return out
        raise ValueError("root JSON must be an object")
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
    if m:
        out = json.loads(m.group(1).strip())
        if isinstance(out, dict):
            return out
        raise ValueError("fenced JSON root must be an object")
    raise ValueError(f"response is not valid JSON (prefix): {raw[:240]!r}")


def _ollama_options() -> dict[str, float | int]:
    """Ollama 専用 `options`（幻覚抑制のため温度は低め）。環境変数で上書き可。"""
    temperature = float(os.environ.get("OLLAMA_TEMPERATURE", "0.15"))
    top_p = float(os.environ.get("OLLAMA_TOP_P", "0.85"))
    opts: dict[str, float | int] = {"temperature": temperature, "top_p": top_p}
    if raw := os.environ.get("OLLAMA_NUM_PREDICT"):
        opts["num_predict"] = int(raw)
    return opts


class OllamaStructuredExtractionGateway(StructuredExtractionGateway):
    """`POST {OLLAMA_HOST}/api/chat` で `format: json` 応答を得て `dict` にする。

    プロンプト文言は `StructuredExtractionPromptBuilder` に委譲し、Ollama 固有ののは HTTP・`options`・モデル名のみとする。
    """

    def __init__(
        self,
        *,
        prompt_builder: StructuredExtractionPromptBuilder | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_sec: float | None = None,
    ) -> None:
        self._prompt = prompt_builder or get_prompt_builder(os.environ.get("TIP_PROMPT_PROFILE"))
        self._base = (base_url or os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
        self._model = model or os.environ.get("OLLAMA_MODEL", "llama3.2")
        if timeout_sec is not None:
            self._timeout = float(timeout_sec)
        else:
            self._timeout = float(os.environ.get("OLLAMA_TIMEOUT_SEC", "120"))

    def infer(self, inp: StructuredExtractionInput) -> StructuredExtractionOutput:
        turns = self._prompt.build(inp)
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": turns.system},
                {"role": "user", "content": turns.user},
            ],
            "stream": False,
            "format": "json",
            "options": _ollama_options(),
        }
        url = f"{self._base}/api/chat"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                res = client.post(url, json=payload)
                if res.status_code >= 400:
                    detail = _ollama_http_error_message(res)
                    hint = ""
                    if res.status_code == 404:
                        hint = (
                            f" モデル '{self._model}' が未登録の可能性が高いです。"
                            f"Ollama を動かしているマシンで `ollama pull {self._model}` を実行してください。"
                        )
                    msg = f"ollama HTTP {res.status_code} {url}: {detail}{hint}"
                    logger.warning("ollama error response: %s", msg)
                    raise RuntimeError(msg)
                body = res.json()
        except RuntimeError:
            raise
        except httpx.HTTPError as exc:
            logger.warning("ollama http error: %s", exc)
            raise RuntimeError(f"ollama request failed: {exc}") from exc
        except httpx.RequestError as exc:
            logger.warning("ollama request error: %s", exc)
            raise RuntimeError(f"ollama unreachable: {exc}") from exc

        msg = body.get("message") or {}
        content = msg.get("content")
        if isinstance(content, dict):
            data = content
        elif isinstance(content, str):
            data = _parse_json_object(content)
        else:
            raise ValueError("unexpected message.content type from ollama")

        fp_src = f"{self._model}|{turns.profile_id}|{turns.user}".encode()
        prompt_fingerprint = hashlib.sha256(fp_src).hexdigest()[:16]
        return StructuredExtractionOutput(
            data=data,
            model_id=f"ollama:{self._model}",
            prompt_fingerprint=prompt_fingerprint,
        )
