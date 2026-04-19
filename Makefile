# context-matching — よく使う操作をルートから実行する
# macOS / Linux 上の Make（BSD / GNU）で利用可。既定ターゲットは help

.DEFAULT_GOAL := help

# 任意: ホストの pnpm が別ストアを指している場合のみ上書き
# export PNPM_STORE_DIR ?= $(HOME)/.pnpm-store/v10

.PHONY: help
help: ## ターゲット一覧を表示する
	@echo "利用可能なターゲット:"
	@echo "  help                   この一覧を表示する"
	@echo "  install                API・Web の依存を入れる（uv sync / pnpm install）"
	@echo "  api-dev                API をホストで起動（:8000）"
	@echo "  web-dev                Web をホストで起動（:5173）"
	@echo "  compose-up             docker compose up --build（API+Web）"
	@echo "  compose-down           docker compose down"
	@echo "  compose-api            docker compose up --build api のみ"
	@echo "  test-api               apps/api で pytest"
	@echo "  build-web              apps/web で本番ビルド"
	@echo "  e2e-install            Playwright Chromium を node_modules 配下に入れる"
	@echo "  e2e                    Web E2E（stub API 同梱。初回は e2e-install）"
	@echo "  test / check           test-api と build-web をまとめて実行"

.PHONY: install
install: ## API・Web の依存を入れる（uv sync / pnpm install）
	cd apps/api && uv sync
	cd apps/web && pnpm install

.PHONY: api-dev
api-dev: ## API をホストで起動する（http://127.0.0.1:8000）
	cd apps/api && uv run uvicorn talent_interview_profile_poc.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: web-dev
web-dev: ## Web をホストで起動する（http://127.0.0.1:5173。API は別ターミナルで api-dev など）
	cd apps/web && pnpm dev

.PHONY: compose-up
compose-up: ## Docker Compose で API+Web を起動する（--build）
	docker compose up --build

.PHONY: compose-down
compose-down: ## Docker Compose のコンテナを止める
	docker compose down

.PHONY: compose-api
compose-api: ## Docker Compose で API のみ起動する（--build）
	docker compose up --build api

.PHONY: test-api
test-api: ## API のユニット・結合テスト（pytest）
	cd apps/api && uv run pytest

.PHONY: build-web
build-web: ## Web の本番ビルド（tsc + vite build）
	cd apps/web && pnpm run build

.PHONY: e2e-install
e2e-install: ## Playwright の Chromium を node_modules 配下に入れる
	cd apps/web && pnpm run test:e2e:install

.PHONY: e2e
e2e: ## Web の E2E（stub API を同梱スクリプトで起動。初回は e2e-install）
	cd apps/web && CI=1 pnpm run test:e2e

.PHONY: test
test: test-api build-web ## API テストと Web ビルドをまとめて実行する

.PHONY: check
check: test-api build-web ## プッシュ前の軽い検証（test と同じ）
