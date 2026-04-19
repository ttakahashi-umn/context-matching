from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class StructuredExtractionInput:
    transcript_text: str
    template_yaml: str
    template_version_id: str


@dataclass(frozen=True, slots=True)
class StructuredExtractionOutput:
    data: dict[str, Any]
    model_id: str
    prompt_fingerprint: str


class StructuredExtractionGateway(Protocol):
    def infer(self, inp: StructuredExtractionInput) -> StructuredExtractionOutput: ...
    """オンデバイス推論の抽象。PoC ではスタブ実装を差し替え可能。"""
