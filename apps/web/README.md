# talent-interview-profile-poc Web

Vite + React 19 + TypeScript strict。API は開発時 `/api` プロキシ経由で参照する。

## ローカル（Docker 以外）

ターミナル 1: `apps/api` で API を起動（ポート 8000）。

ターミナル 2:

```bash
cd apps/web
pnpm install
pnpm dev
```

## Docker

リポジトリルートから `docker compose up --build` で API と Web を起動する。
