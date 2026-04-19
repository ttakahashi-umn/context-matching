# Design Document: project-registration-poc

---
**Purpose**: 案件（募集単位）の永続化と REST・最小 Web UI を、既存 `talent-interview-profile-poc` と同一モノレポ内で独立境界として追加する契約を固定する。
---

## Overview

**目的**: 運用者が **案件** を登録・一覧・参照・更新でき、将来のマッチング機能が参照できる **最小マスタ** を提供する。

**利用者**: PoC 運用者（案件データの登録・更新）。

**影響**: `apps/api` に **新規 Python パッケージ**（本書では `project_registration` とする）を `src/` 直下に追加し、既存 `talent_interview_profile_poc` と **同一プロセスの FastAPI アプリ** にマウントする。永続化は **SQLite** を継続利用し、**同一 DB ファイル**上に案件用テーブルを追加する（単一エンジン・トランザクション境界は案件側ユースケース単位）。`apps/web` に案件用の **一覧・登録・詳細（編集）** 画面とナビ導線を追加する。

### Goals

- レイヤード構成（プレゼンテーション / アプリケーション / ドメイン / インフラ）を既存 PoC と同趣旨で維持する。
- REST で `POST/GET/GET collection/PATCH` を提供し、OpenAPI に現れる。
- 最小 Web UI で Requirement 4 を満たす。

### Non-Goals

- マッチング、人材との関連テーブル、権限、監査ログの完成品。

## Boundary Commitments

### This Spec Owns

- **案件（Case）** エンティティの永続化モデルと検証規則。
- 案件用 **REST ルーター** と HTTP DTO。
- 案件用 **アプリケーションサービス** と **リポジトリ抽象の具象**（SQLAlchemy）。
- **案件用 Web ページ** と HTTP クライアント呼び出し。

### Out of Boundary

- 人材・面談・テンプレ・抽出・プロフィールのドメインルール変更（本 spec のタスクでは触れない）。
- クラウド LLM、非 SQLite ストアへの移行。

### Allowed Dependencies

- **上流**: 既存の `uv` / `pnpm` ツールチェーン、ルート `Makefile`。
- **ランタイム**: Python 3.14、FastAPI、Pydantic v2、SQLAlchemy 2.x、React 19 + Vite + TypeScript strict。

### Revalidation Triggers

- 案件の必須属性集合の変更。
- REST パス `/cases` の契約変更。

## Architecture

### Pattern

**レイヤードアーキテクチャ**（既存 PoC と同一パターン）。`project_registration` パッケージ内に `presentation` / `application` / `domain` / `infrastructure` を置く。

### Composition Root

- **推奨**: `talent_interview_profile_poc.main` から `project_registration` のルータを **`app.include_router(..., prefix="/cases")`** のように取り込む（または同等のプレフィクスで **人材側 `/talents` と URL 衝突しない** こと）。
- データベースセッション／エンジンは **共有**（同一 `database_url()`）でよい。案件テーブルと人材テーブルは **外部キーで結ばない**（本フェーズ）。

### Logical Data Model

**Case（案件）**（論理名。実装クラス名は `Case` または `ProjectCase` 等でよいが、REST リソース名は `cases`）

| 属性 | 型（論理） | 必須 | 説明 |
|------|------------|------|------|
| id | UUID | システム | 識別子 |
| title | string | はい | 一覧・参照用の短い題名（最大長は要件の検証に合わせ定数化） |
| description | string | はい | 募集内容・条件の本文（最大バイト数を定数で上限、超過は 422） |
| status | enum | はい | 例: `draft` / `open`（将来拡張可能な列挙） |
| created_at / updated_at | datetime | システム | 監査最小 |

### REST 契約（案）

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/cases` | 案件作成。201 + 本文に id |
| GET | `/cases` | 一覧（要約フィールド） |
| GET | `/cases/{case_id}` | 詳細 |
| PATCH | `/cases/{case_id}` | 部分更新（title / description / status のサブセット） |

ステータスコードは既存 PoC と整合（404 / 422 等）。OpenAPI のタグは `cases` など人材側と分離。

### Web

- **パス例**: `/cases` 一覧、`/cases/:caseId` 詳細＋編集フォーム、登録は右スライドまたは専用フォーム（`RegisterSlideOver` の再利用を検討）。
- **API 基底**: 既存と同様 `/api` プロキシ。`client.ts` に案件用メソッドを追加するか、パス文字列で `apiJson` を呼ぶ。

### Testing

- **API**: `pytest` でサービス層とルータ結合（人材 PoC の `tests/` パターンに倣う）。配置は `apps/api/tests/test_cases_*.py` 等。
- **Web**: 本 spec の必須ではないが、既存 E2E にならうなら `make e2e` の拡張はタスクで任意化可能。

## File Structure Plan（案）

```
apps/api/src/
├── talent_interview_profile_poc/   # 既存（本 spec では原則変更しない）
└── project_registration/
    ├── __init__.py
    ├── main_router.py              # APIRouter のエクスポートのみ（組み込み用）
    ├── settings.py                 # 必要なら案件専用定数（上限バイト等）
    ├── presentation/
    ├── application/
    ├── domain/
    └── infrastructure/

apps/web/src/
├── presentation/pages/             # CasesPage.tsx, CaseDetailPage.tsx 等を追加
├── presentation/routes/paths.ts    # paths.cases を追加
└── App.tsx                         # ナビに「案件」を追加
```

## Risk / Notes

- **同一 DB**: マイグレーション戦略は既存と同様 `create_all` 前提なら、新テーブル追加のみ。スキーマ変更時は README に倣い開発用 DB ファイル削除の注意を書く。
- **パッケージ名**: 実装時に `project_registration` と `talent_interview_profile_poc` の import 循環を避け、composition root は一方通行に集約する。
