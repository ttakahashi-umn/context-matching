# 技術スタック

## アーキテクチャ

**`talent-interview-profile-poc`**（`apps/api` / `apps/web`）は **実装済み**のモノレポ構成である。レイヤ境界・REST・推論ゲートウェイの詳細は **`.kiro/specs/talent-interview-profile-poc/design.md`** を正とする。

**`project-registration-poc`**（案件マスタの最小縦割り）は **仕様済み・実装はこれから** である。同一モノレポ内に **`project_registration` パッケージ**（案）を追加し、REST `/cases` と最小 Web を **既存 FastAPI アプリへマウント**する方針。詳細は **`.kiro/specs/project-registration-poc/design.md`** を正とする。

リポジトリ内の **他プロダクト領域**（マッチング本丸など）のスタックは本ファイルでは未確定のまま追記できる。

## コア技術（上記 PoC の実態・2026 時点）

- **言語**: Python 3.14（API）、TypeScript strict（Web）
- **フレームワーク／ランタイム**: FastAPI、Vite + React 19
- **データストア**: SQLite（単一ファイル想定。`design.md` / ルート `README.md` と整合）

## 選定時に優先したい原則

- **型安全**: 可能な限り静的型付けと厳格なチェックで、マッチングロジックのバグを早期に検出する。
- **テスト容易性**: ドメインロジックを UI・インフラから切り離し、自動テストで回帰を守る。
- **段階的デリバリー**: 小さな縦割りリリースができる構成にする。

## 開発標準（PoC 追記分）

### 型安全性

PoC では **TypeScript strict**（`any` 禁止）および **Python 型ヒント + Pydantic v2** を採用している（詳細は `design.md`）。

### コード品質

PoC では `pyproject` / `tsconfig` に従い、CI や pre-commit の有無はリポジトリの実装に合わせて拡張する。

### テスト

PoC API は **`pytest`** でサービス層・ルータ結合を中心に検証する（`apps/api/tests/`）。E2E は仕様上任意（`tasks.md` 9.3）。

## 開発環境

### 必要なツール

PoC 開発では **`uv`**（Python）と **`pnpm`**（Web）を用いる（各 `apps/*/README.md` およびルート `README.md` を参照）。

### よく使うコマンド

```bash
# API（例）
cd apps/api && uv run pytest tests/ -q

# Web（例）
cd apps/web && pnpm run build
```

## 主要な技術判断（メモ）

- スタックは **README とビジネス要件に整合する形** で決める（無理な技術先行をしない）。
- 判断が変わったら、差分と理由を本ファイルに追記する（置き換えではなく履歴として残してよい）。

---

_依存の列挙ではなく、標準と判断のパターンを残す。_
