# context-matching

人材とプロジェクトとをマッチングさせるサービス。

## アプリ（PoC）

| ディレクトリ | 内容 |
|--------------|------|
| `apps/api` | FastAPI（Python 3.14 + `uv`） |
| `apps/web` | Vite + React 19 + TypeScript（`pnpm`） |

## Docker でローカル起動

リポジトリルートで:

```bash
docker compose up --build
```

- API: http://localhost:8000/health  
- Web: http://localhost:5173/（`/api` を API にプロキシ）  
- **Ollama は compose に含めません。** 下記 **「Ollama（Mac へのローカルインストールと llama3.2）」** のとおりホストで Ollama を起動し、**`ollama pull llama3.2`** 済みであることを前提に、API コンテナから **`http://host.docker.internal:11434`** へ接続します（`docker-compose.yml` の `OLLAMA_HOST`）。

Compose では API に **`TIP_INFERENCE_ENGINE=ollama`**、**`TIP_PROMPT_PROFILE=ja_flat_json`**、**`OLLAMA_HOST=http://host.docker.internal:11434`**、**`OLLAMA_MODEL=llama3.2`** が設定されています。**スタブに戻す**ときは `docker-compose.override.yml` 等で **`TIP_INFERENCE_ENGINE=stub`** にするか **`TIP_FORCE_STUB_INFERENCE=1`** を付けると確実です。

`docker compose up` では **`apps/api/src` と `apps/web/src`・`apps/web/public` 等をボリュームマウント**しており、**Python / TS・TSX / 静的ファイルの変更は再ビルドなしでコンテナ内に反映**されます（API は `uvicorn --reload`、Web は Vite の HMR。ファイル監視は `CHOKIDAR_USEPOLLING` でポーリング）。

人材テーブルのカラムを変更した場合は、既存の **`data/*.db` を削除**してから API を起動し直すと、`create_all` で新スキーマが作成されます。

次の変更をしたときは **イメージの再ビルド**が必要です。

- API: `pyproject.toml` / `uv.lock` の依存変更
- Web: `package.json` / `pnpm-lock.yaml` の依存変更

単体で API のみ起動する場合: `docker compose up --build api`（**ホストの Ollama が起動していること**を前提にします。Ollama を使わず API だけ試す場合は **`TIP_INFERENCE_ENGINE=stub`** にするか **`TIP_FORCE_STUB_INFERENCE=1`** を API の環境に追加してください）

## Ollama（Mac へのローカルインストールと llama3.2）

**Docker Compose の API は、ホストで動かす Ollama に接続する前提です**（Metal を活かしやすく、compose に Ollama サービスは含めません）。

### 1. Ollama のインストール（macOS）

次のいずれかでインストールします。

**公式インストーラ（推奨）**

1. [Ollama のダウンロードページ](https://ollama.com/download)から **macOS 用**を取得する。  
2. 開いて **アプリケーションフォルダにドラッグ**する（指示に従う）。  
3. **Ollama** を起動する。メニューバーにアイコンが出れば、バックグラウンドで **`ollama serve`** に相当するサーバーが待ち受けている状態です（既定で **`http://127.0.0.1:11434`**）。

**Homebrew を使う場合**

```bash
brew install --cask ollama
```

その後、**アプリケーションから Ollama を起動**するか、ターミナルで `ollama serve` を実行してサーバーを立ち上げます。

### 2. モデル llama3.2 の取得

ターミナルで次を実行し、本リポジトリの compose / API 既定（`OLLAMA_MODEL=llama3.2`）と同じ名前のモデルを取得します。

```bash
ollama pull llama3.2
```

完了を確認する例:

```bash
ollama list
```

動作確認の例（対話で終了は `Ctrl+D` など）:

```bash
ollama run llama3.2 "こんにちは"
```

抽出結果の文字化け・幻覚を抑えるため、API 側の Ollama 呼び出しは **日本語の厳格な指示**と **低い `temperature`（既定 0.15）** を使っています。さらに抑えたい場合は環境変数 **`OLLAMA_TEMPERATURE`**（例: `0.05`）や、より余裕のあるモデルへの変更を検討してください（`apps/api/README.md` の表参照）。

### 3. `docker compose` で API を動かすとき

ルートの **`docker-compose.yml`** が上記と同じ接続先になるよう、API サービスに **`TIP_INFERENCE_ENGINE=ollama`**・**`TIP_PROMPT_PROFILE=ja_flat_json`**・**`OLLAMA_HOST=http://host.docker.internal:11434`**・**`OLLAMA_MODEL=llama3.2`** を設定済みです。  
**ホスト側で Ollama を起動したうえで** `docker compose up` してください（ポート **11434** で待ち受け）。

## 抽出テンプレート（YAML）

面談テキストに対して「どの観点を構造化するか」を宣言する YAML を API で登録し、抽出実行時に渡します。PoC の検証ルールは次のとおりです。

- **ルート**: 必ず **マッピング（`key: value`）**。配列だけの YAML は不可。
- **`version`**: 推奨。文字列で書くと、その値がテンプレ版の **ラベル**（一覧に出る識別子）として保存されます。
- **`purpose`**: **必須**。非空の文字列で、このテンプレの **用途**（一覧・選択 UI に表示）を書きます。
- **値の型**: 文字列・数値・真偽・子マッピング、または上記の **JSON 互換な配列**（要素は文字列など）に限定されます。

### 実例（最小）

```yaml
version: "1.0.0-poc"
purpose: "PoC 用の最小サンプル"
fields:
  summary: string
  skills:
    type: array
    items: string
```

リポジトリ内のファイル: [`examples/templates/default_template.yaml`](examples/templates/default_template.yaml)

### 実例（汎用 IT エンジニア面談）

採用・キャリア面談の文字起こしから、技術広度・設計・運用・協業などを拾うための観点テンプレです。

- ソース（API パッケージ同梱・**起動時シード**に使用）: [`apps/api/src/talent_interview_profile_poc/seed/it_engineer_interview.yaml`](apps/api/src/talent_interview_profile_poc/seed/it_engineer_interview.yaml)
- コピー用（リポジトリ閲覧用・中身は同一）: [`examples/templates/it_engineer_interview.yaml`](examples/templates/it_engineer_interview.yaml)

### シードデータ（自動登録）

API 起動時（`lifespan`）に、DB に **`version: "seed-it-engineer-v1"`** のテンプレが **1 件も無い**場合だけ、上記 IT エンジニア用 YAML を **自動で登録**します。既に同名ラベルがある場合は何もしません（手動編集の上書きはしません）。

既存テンプレート行の YAML を置き換える場合は **`PATCH /templates/{template_version_id}`**（本文 `{ "yaml_text": "..." }`、検証は POST 登録と同一）。ルート `version` が他行のラベルと衝突する更新は **409** になります。

## Docker 以外

`apps/api/README.md` と `apps/web/README.md` を参照。
