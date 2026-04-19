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
