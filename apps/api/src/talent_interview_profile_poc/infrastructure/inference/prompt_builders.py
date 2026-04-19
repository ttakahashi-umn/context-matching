"""`StructuredExtractionPromptBuilder` の登録と解決。"""

from __future__ import annotations

import os

from talent_interview_profile_poc.domain.abstractions.extraction_prompting import (
    ExtractionChatTurns,
    StructuredExtractionPromptBuilder,
)
from talent_interview_profile_poc.domain.abstractions.inference import StructuredExtractionInput

_PROFILE_JA_FLAT_JSON = "ja_flat_json"


class JaFlatJsonPromptBuilder:
    """日本語指示でフラット JSON（template_version_id + extraction_targets 各キー）を促すプロンプト。"""

    def profile_id(self) -> str:
        return _PROFILE_JA_FLAT_JSON

    def build(self, inp: StructuredExtractionInput) -> ExtractionChatTurns:
        system = (
            "あなたは面談の文字起こしから、指定された観点だけを抜き出してJSONにするツールです。"
            "JSON以外の文字は一切出力しません。ユーザーの指示に厳密に従ってください。"
        )
        user = (
            "## 役割\n"
            "次の「テンプレYAML」に含まれる `extraction_targets:` 直下のキー（例: career_summary, tech_stack）"
            "ごとに、面談テキストから当てはまる内容を日本語の短文で書きます。\n\n"
            "## 出力JSONの形（厳守）\n"
            "- ルートはフラットなオブジェクト1つだけ。前後に説明文やマークダウンは禁止。\n"
            "- 必ずキー `template_version_id` を含め、その値は次のUUID文字列と**完全一致**:\n"
            f"  {inp.template_version_id}\n"
            "- それ以外のキーは、テンプレYAMLの `extraction_targets:` に並んでいる**キー名だけ**"
            "（ネストした `extraction_targets` オブジェクトは作らない）。\n"
            "- ルートに `version` / `purpose` / `meta` を出力しない。YAMLの文言をコピーして改変したりしない。\n"
            "- 各観点の値はすべて**文字列**。面談テキストに**明示的な根拠がある内容のみ**。"
            " 推測で細部を捏造しない。根拠がない場合は空文字列 `\"\"`。\n"
            "- すべて**自然な日本語**（面談にない言語の混入・意味不明な記号の羅列・Unicodeエスケープの乱用は禁止）。\n"
            "- 値は面談に書かれた事実の要約に留める（テンプレの `prompt_hint` は観点の説明であり、出力にそのまま貼らない）。\n\n"
            "## テンプレYAML（構造と観点の参考）\n"
            f"{inp.template_yaml}\n\n"
            "## 面談テキスト（ここだけが根拠）\n"
            f"{inp.transcript_text}\n"
        )
        return ExtractionChatTurns(system=system, user=user, profile_id=self.profile_id())


def get_prompt_builder(profile_id: str | None) -> StructuredExtractionPromptBuilder:
    """環境変数 `TIP_PROMPT_PROFILE` 等からビルダを返す。未知の ID は拒否する。"""
    pid = (profile_id or os.environ.get("TIP_PROMPT_PROFILE") or _PROFILE_JA_FLAT_JSON).strip().lower()
    if pid == _PROFILE_JA_FLAT_JSON:
        return JaFlatJsonPromptBuilder()
    raise ValueError(f"unknown prompt profile: {pid!r} (supported: {_PROFILE_JA_FLAT_JSON!r})")
