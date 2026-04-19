"""開発・Docker 向けの決定的スタブ推論（外部ネットワーク不使用）。"""

from __future__ import annotations

import hashlib

from talent_interview_profile_poc.domain.abstractions.inference import (
    StructuredExtractionGateway,
    StructuredExtractionInput,
    StructuredExtractionOutput,
)


class StubStructuredExtractionGateway(StructuredExtractionGateway):
    """テンプレと面談テキストから安定した JSON を返す（PoC デモ用）。"""

    def infer(self, inp: StructuredExtractionInput) -> StructuredExtractionOutput:
        fp_src = f"{inp.template_version_id}|{inp.template_yaml}".encode()
        prompt_fingerprint = hashlib.sha256(fp_src).hexdigest()[:16]
        digest = hashlib.sha256(inp.transcript_text.encode()).hexdigest()[:12]
        data = {
            "summary": f"stub extraction for transcript digest {digest}",
            "template_version_id": inp.template_version_id,
            "skills": ["communication", "problem_solving"],
        }
        return StructuredExtractionOutput(
            data=data,
            model_id="stub-mlx-compatible",
            prompt_fingerprint=prompt_fingerprint,
        )
