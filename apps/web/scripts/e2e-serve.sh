#!/usr/bin/env bash
# Playwright 用: stub 推論 + 専用 SQLite で API を起動し、その後 Vite を同一プロセスで待機する。
set -euo pipefail

WEB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_ROOT="$WEB_ROOT/../api"
DB_PATH="/tmp/tip_e2e_playwright.db"

rm -f "$DB_PATH"
export TIP_INFERENCE_ENGINE=stub
export TIP_DATABASE_URL="sqlite+pysqlite:///${DB_PATH}"

cd "$API_ROOT"
uv run uvicorn talent_interview_profile_poc.main:app --host 127.0.0.1 --port 8765 &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

for _ in $(seq 1 120); do
  if curl -sf "http://127.0.0.1:8765/health" >/dev/null; then
    break
  fi
  sleep 0.25
done

cd "$WEB_ROOT"
export VITE_API_PROXY_TARGET=http://127.0.0.1:8765
pnpm exec vite --host 127.0.0.1 --port 5173
