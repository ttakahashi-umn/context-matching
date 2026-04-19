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

`docker compose up` では **`apps/api/src` と `apps/web/src`・`apps/web/public` 等をボリュームマウント**しており、**Python / TS・TSX / 静的ファイルの変更は再ビルドなしでコンテナ内に反映**されます（API は `uvicorn --reload`、Web は Vite の HMR。ファイル監視は `CHOKIDAR_USEPOLLING` でポーリング）。

人材テーブルのカラムを変更した場合は、既存の **`data/*.db` を削除**してから API を起動し直すと、`create_all` で新スキーマが作成されます。

次の変更をしたときは **イメージの再ビルド**が必要です。

- API: `pyproject.toml` / `uv.lock` の依存変更
- Web: `package.json` / `pnpm-lock.yaml` の依存変更

単体で API のみ起動する場合: `docker compose up --build api`

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

## Docker 以外

`apps/api/README.md` と `apps/web/README.md` を参照。
