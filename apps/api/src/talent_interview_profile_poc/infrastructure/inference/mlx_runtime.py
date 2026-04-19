"""`mlx-lm` をインストールした環境向けの実行時ゲートウェイ（任意依存）。"""

from __future__ import annotations

from talent_interview_profile_poc.domain.abstractions.inference import (
    StructuredExtractionGateway,
    StructuredExtractionInput,
    StructuredExtractionOutput,
)
from talent_interview_profile_poc.domain.exceptions import InferenceError
from talent_interview_profile_poc.infrastructure.inference.stub_llm_gateway import (
    StubStructuredExtractionGateway,
)


class MlxLmStructuredExtractionGateway(StructuredExtractionGateway):
    """mlx-lm の import に成功したらスタブへ委譲しつつモデル識別子だけ MLX 系にする PoC ブリッジ。

    実モデル読み込みと生成ループは後続タスクで拡張可能。外部ネットワークは使用しない。
    """

    def __init__(self) -> None:
        import mlx_lm  # type: ignore[import-not-found]  # noqa: F401

        self._stub = StubStructuredExtractionGateway()
        self._package = "mlx-lm"

    def infer(self, inp: StructuredExtractionInput) -> StructuredExtractionOutput:
        out = self._stub.infer(inp)
        if not out.data:
            raise InferenceError("MLX ブリッジ: スタブが空結果を返しました")
        return StructuredExtractionOutput(
            data=out.data,
            model_id=f"mlx-lm-bridge::{self._package}",
            prompt_fingerprint=out.prompt_fingerprint,
        )
