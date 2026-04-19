"""後方互換: ゲートウェイ組み立ては `inference_gateway_factory` に集約。"""

from __future__ import annotations

from talent_interview_profile_poc.infrastructure.inference.inference_gateway_factory import (
    build_structured_extraction_gateway,
)

__all__ = ["build_structured_extraction_gateway"]
