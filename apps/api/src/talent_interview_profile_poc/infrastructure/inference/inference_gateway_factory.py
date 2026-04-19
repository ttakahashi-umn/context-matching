"""`StructuredExtractionGateway` の具体実装を環境変数で選択するファクトリ。"""

from __future__ import annotations

import logging
import os

from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionGateway
from talent_interview_profile_poc.infrastructure.inference.stub_llm_gateway import (
    StubStructuredExtractionGateway,
)

logger = logging.getLogger(__name__)


def _resolve_inference_engine() -> str:
    """推論エンジン識別子: stub | ollama | mlx。

    優先: `TIP_FORCE_STUB_INFERENCE` → `TIP_INFERENCE_ENGINE` → 従来の `TIP_USE_OLLAMA` / `TIP_USE_MLX` → 既定 stub。
    """
    if os.environ.get("TIP_FORCE_STUB_INFERENCE", "").lower() in {"1", "true", "yes"}:
        return "stub"
    raw = (os.environ.get("TIP_INFERENCE_ENGINE") or "").strip().lower()
    if raw in {"stub", "ollama", "mlx"}:
        return raw
    if os.environ.get("TIP_USE_OLLAMA", "").lower() in {"1", "true", "yes"}:
        return "ollama"
    if os.environ.get("TIP_USE_MLX", "").lower() in {"1", "true", "yes"}:
        return "mlx"
    return "stub"


def build_structured_extraction_gateway() -> StructuredExtractionGateway:
    engine = _resolve_inference_engine()
    profile = os.environ.get("TIP_PROMPT_PROFILE", "ja_flat_json")
    logger.info("structured extraction: engine=%s prompt_profile=%s", engine, profile)

    if engine == "stub":
        return StubStructuredExtractionGateway()

    if engine == "ollama":
        from talent_interview_profile_poc.infrastructure.inference.ollama_llm_gateway import (
            OllamaStructuredExtractionGateway,
        )

        return OllamaStructuredExtractionGateway()

    if engine == "mlx":
        try:
            from talent_interview_profile_poc.infrastructure.inference import mlx_runtime

            return mlx_runtime.MlxLmStructuredExtractionGateway()
        except Exception as exc:
            logger.warning(
                "TIP_INFERENCE_ENGINE=mlx だが MLX ゲートウェイを初期化できませんでした: %s。スタブへフォールバックします。",
                exc,
            )
            return StubStructuredExtractionGateway()
