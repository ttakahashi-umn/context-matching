# talent-interview-profile-poc API

FastAPI ベースの PoC API。レイヤード構成は `design.md` に従い後続で拡張する。

## ローカル（Docker 以外）

```bash
cd apps/api
uv sync
uv run uvicorn talent_interview_profile_poc.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

リポジトリルートから `docker compose up --build api` で単体起動できる。

## テンプレートシード

起動時に IT エンジニア面談用テンプレ（`version: seed-it-engineer-v1`）が未登録なら自動投入されます。仕様と YAML 実例はリポジトリルートの **`README.md`（抽出テンプレート）** を参照してください。

## 構造化抽出（推論バックエンド）

ゲートウェイは **`inference_gateway_factory.build_structured_extraction_gateway()`** で組み立てる。プロンプト文言は **`StructuredExtractionPromptBuilder`**（ドメイン抽象）の実装に分離し、エンジン固有の HTTP やモデル名とは切り離す。

### 推論エンジン（`TIP_INFERENCE_ENGINE`）

| 値 | 説明 |
|----|------|
| `stub` | 決定的スタブ（外部 HTTP なし） |
| `ollama` | `OllamaStructuredExtractionGateway`（`/api/chat`） |
| `mlx` | `mlx_runtime.MlxLmStructuredExtractionGateway`（失敗時はスタブへフォールバック） |

解決の優先順位: **`TIP_FORCE_STUB_INFERENCE`** → **`TIP_INFERENCE_ENGINE`** → 従来互換の **`TIP_USE_OLLAMA` / `TIP_USE_MLX`** → 既定 **`stub`**。

### プロンプトプロファイル（`TIP_PROMPT_PROFILE`）

| 値 | 説明 |
|----|------|
| `ja_flat_json` | 日本語指示でフラット JSON を促す（既定） |

未知の値は起動時に拒否される。追加プロファイルは `infrastructure/inference/prompt_builders.py` に実装を足す。

### Ollama 専用の環境変数（`TIP_INFERENCE_ENGINE=ollama` のとき）

1. [Ollama](https://ollama.com/) を起動し、利用モデルを `ollama pull` する。
2. 次の変数で接続先・生成オプションを調整する。

| 変数 | 既定 | 説明 |
|------|------|------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama のベース URL |
| `OLLAMA_MODEL` | `llama3.2` | `POST /api/chat` の `model` |
| `OLLAMA_TIMEOUT_SEC` | `120` | 1 リクエストのタイムアウト（秒） |
| `OLLAMA_TEMPERATURE` | `0.15` | `options.temperature` |
| `OLLAMA_TOP_P` | `0.85` | `options.top_p` |
| `OLLAMA_NUM_PREDICT` | （未設定） | 設定時のみ `options.num_predict` |

Docker 内の API から **ホスト macOS の Ollama** を使う場合は **`OLLAMA_HOST=http://host.docker.internal:11434`**（Docker Desktop on Mac の典型例）。ルート **`docker-compose.yml`** の API は **`TIP_INFERENCE_ENGINE=ollama`** と併せてこの形を想定している。

**注意:** Ollama 有効時は抽出が **ローカル HTTP** に依存する。`/api/chat` が **404** のときは多くの場合 **指定モデルが未 `pull`**。

### MLX

`TIP_INFERENCE_ENGINE=mlx` かつ `mlx-lm` が import 可能なとき MLX ブリッジを試す。実装は `infrastructure/inference/mlx_runtime.py`。後続で同じ **`StructuredExtractionPromptBuilder`** を MLX 経路に渡す拡張が可能。
