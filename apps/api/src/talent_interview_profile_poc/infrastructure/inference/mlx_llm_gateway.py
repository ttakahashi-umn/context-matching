"""オンデバイス推論ゲートウェイのファクトリ（既定はスタブ、MLX は明示有効化）。"""

from __future__ import annotations

import logging
import os

from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionGateway
from talent_interview_profile_poc.infrastructure.inference.stub_llm_gateway import (
    StubStructuredExtractionGateway,
)

logger = logging.getLogger(__name__)


def build_structured_extraction_gateway() -> StructuredExtractionGateway:
    """`TIP_USE_MLX=1` かつ `mlx_runtime` が利用可能なときのみ MLX 経路を試す。それ以外はスタブ。"""
    if os.environ.get("TIP_FORCE_STUB_INFERENCE", "").lower() in {"1", "true", "yes"}:
        return StubStructuredExtractionGateway()

    if os.environ.get("TIP_USE_MLX", "").lower() in {"1", "true", "yes"}:
        try:
            from talent_interview_profile_poc.infrastructure.inference import mlx_runtime

            return mlx_runtime.MlxLmStructuredExtractionGateway()
        except Exception as exc:
            logger.warning(
                "TIP_USE_MLX が指定されましたが MLX ゲートウェイを初期化できませんでした: %s。スタブを使用します。",
                exc,
            )
            return StubStructuredExtractionGateway()

    return StubStructuredExtractionGateway()
