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

単体で API のみ起動する場合: `docker compose up --build api`

API イメージは **`--no-editable`** でビルドしているため、**コード変更をコンテナに反映するには `docker compose build api`（または `--build`）で再ビルド**する。ホストの `src` をマウントして即時反映したい場合は `docker-compose.yml` にボリュームを追加し、editable に戻す（その場合は `:ro` にしないこと）。

## Docker 以外

`apps/api/README.md` と `apps/web/README.md` を参照。
