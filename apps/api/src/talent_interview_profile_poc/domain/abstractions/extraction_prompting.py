"""構造化抽出へ渡すプロンプト（チャット系）の組み立て抽象。

具体文言は推論エンジン（Ollama / MLX 等）に依存しないよう、インフラ層のビルダ実装に置く。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionInput


@dataclass(frozen=True, slots=True)
class ExtractionChatTurns:
    """チャット API 向けの system / user メッセージと、追跡用プロファイル識別子。"""

    system: str
    user: str
    profile_id: str


class StructuredExtractionPromptBuilder(Protocol):
    """テンプレ YAML と面談テキストから、推論エンジンへ送るメッセージを組み立てる。"""

    def profile_id(self) -> str:
        """`TIP_PROMPT_PROFILE` 等と一致する識別子。"""
        ...

    def build(self, inp: StructuredExtractionInput) -> ExtractionChatTurns:
        ...
