# Research & Design Decisions

---
**Purpose**: 本 PoC のアーキテクチャ調査と、`design.md` に載せきれない比較・根拠の退避先。
---

## Summary

- **Feature**: `talent-interview-profile-poc`
- **Discovery Scope**: New Feature（当初グリーンフィールド。**現在は** `apps/api` / `apps/web` に実装あり。以降の記述は採用判断の記録として保持する）。
- **Key Findings**:
  - オンデバイス推論は **Apple Silicon 上の MLX（`mlx-lm`）** が PoC の実装速度と再現性のバランスに有利。厳密な **CoreML** はモデル変換・パイプライン構築コストが高く、**第 2 候補／スパイク**とした方がリスクが散らせる。
  - **再現性と CI** のため、環境未設定時のコード既定は **`stub`** とし、本番志向のオンデバイス推論は **`TIP_INFERENCE_ENGINE=mlx`**（および Docker 等での **Ollama**）で明示的に有効化する方針が採用された。
  - 永続化は **単一 SQLite ファイル** で十分。抽出中の競合は **セッション単位の排他**（DB 上のステータスまたはトランザクション）で要件 4 の「整合性が判断できる状態」を満たしやすい。
  - 最小 UI は **Vite + React + TypeScript（strict）** とし、API は **FastAPI + OpenAPI** で契約を固定すると、フロントとバックの並行実装がしやすい。

## Research Log

### オンデバイス推論（MLX と CoreML）

- **Context**: ステークホルダー意向として Mac 上オンデバイス、CoreML 含む Apple 系を優先したい。
- **Sources Consulted**: Apple MLX プロジェクト概要、PoC での一般的な LLM 推論パターン（社内知識に基づく判断）。
- **Findings**:
  - MLX は Apple Silicon 向けに最適化され、Python からの統合が比較的容易。
  - CoreML は変換パイプラインとモデル選定の固定化が必要で、探索初期の PoC では変更コストが高い。
- **Implications**: `design.md` では **インフラストラクチャ層に MLX ゲートウェイ**を置き、**`inference_gateway_factory`** で **stub / Ollama / MLX** を切り替える。**CoreML 変換モデル**は同一 `StructuredExtractionGateway` 抽象の別実装として後続スパイクに回す（レイヤード構成のまま差し替え）。

### 同時実行と SQLite

- **Context**: 要件 4 の「抽出実行中に競合更新が起きないよう」運用者が整合性を判断できる状態。
- **Findings**:
  - PoC 規模では **同一セッションに対する同時抽出リクエストを拒否または直列化**するのが単純。
  - WAL モードの SQLite で読取と単一書き込みを分離できる。
- **Implications**: `ExtractionRun` に `running` ステータスを置き、同一 `interview_session_id` で `running` が存在する間は新規実行を `409` 相当で返す方針とする。

## Architecture Pattern Evaluation

| Option | 説明 | 利点 | リスク | メモ |
|--------|------|------|--------|------|
| A: FastAPI + SQLite + MLX | API 一体型バックエンド + 単一 DB | 実装が速い、デプロイが単純 | API プロセスと推論が同一リソース | PoC に最適（実装では **stub / Ollama / MLX** を環境で選択） |
| B: SwiftUI + CoreML ネイティブ | フル macOS アプリ | CoreML への距離が近い | UI・永続・パイプラインを一括で抱え初期コスト大 | 将来検討 |
| C: クラウド LLM | 外部 API | 品質は出やすい | オンデバイス要件と衝突 | 本 PoC では採用しない |

## Design Decisions

### Decision: 推論をゲートウェイ抽象＋環境選択（stub / Ollama / MLX）に置く

- **Context**: 面談テキストからの構造化抽出を Mac 上で完結させたい一方、**開発・CI では外部依存なし**で通したい。
- **Alternatives Considered**: CoreML のみで完結；クラウド API を既定にする。
- **Selected Approach**: ドメインに **`StructuredExtractionGateway`** と **`StructuredExtractionPromptBuilder`** 抽象を置き、インフラ層の **`inference_gateway_factory`**（`TIP_INFERENCE_ENGINE`）が **`stub_llm_gateway`** / **`ollama_llm_gateway`** / **`mlx_runtime`**（MLX）を組み立てる。プロンプト文言は **`prompt_builders`**（`TIP_PROMPT_PROFILE`）に集約する。**環境未設定時のコード既定は `stub`**。オンデバイス品質検証時は **`mlx`**、ホスト LLM 連携時は **`ollama`** を選ぶ。CoreML は同一抽象の別実装として後続スパイクに回す。
- **Rationale**: PoC の検証サイクルを短くし、役員デモまでの経路を確保しつつ、再現可能な既定パスを維持する。
- **Trade-offs**: CoreML への忠実度は下がるが、「Apple Silicon 上のオンデバイス」という意図は **`mlx` 選択時**に満たしやすい。
- **Follow-up**: 実装スパイクでモデルサイズ・レイテンシを測定し、`tech.md` を更新する。

### Decision: フロントは React（strict）、バックは Python 型付き

- **Context**: steering は型安全・テスト容易性を重視。フロント言語は未固定。
- **Selected Approach**: TypeScript strict + Pydantic v2。
- **Rationale**: UI とドメインロジックの関心を分離しつつ、双方で静的な契約を持てる。
- **Follow-up**: OpenAPI から TypeScript クライアントを生成するか、手書きの薄いクライアントにするかは実装タスクで決定。

## Risks & Mitigations

- **モデル選定の遅延** — 最初は小規模指示追従モデルで開始し、精度不足ならテンプレ側で観点数を絞る。
- **抽出結果のブレ** — 温度 0 に近い設定、入力ハッシュとプロンプトバージョンの記録で再現性を担保。
- **個人情報の誤送信** — クラウド有償 LLM を既定にせず、**コード既定の `stub`** およびローカル推論経路を中心にし、ログに原文を出しすぎない方針を `design.md` の運用に記載。

## References

- [MLX](https://ml-explore.github.io/mlx/) — Apple Silicon 向け配列フレームワーク（調査の出発点）。
- [FastAPI](https://fastapi.tiangolo.com/) — OpenAPI ファーストの API 構築。
