# Research / Gap Analysis: project-registration-poc

**実施日**: 2026-04-20  
**入力**: `requirements.md`、既存 `apps/api`・`apps/web`、本 spec の `design.md`  
**前提**: `spec.json` では要件・設計・タスクが承認済み（gap は実装直前の差分把握用）。

---

## 1. 分析サマリー（要約）

- **案件ドメインの実装資産はゼロ**（`project_registration`、`/cases`、Web の案件パスはコードベースに未出現）。要件 1〜5のうち、**機能面はすべてギャップ（Missing）**であり、人材 PoC と同型の縦割りを新規に積む必要がある。
- **統合の肝**は SQLite の **`create_all` が参照する `Base.metadata` が現状 `talent_interview_profile_poc` の `DeclarativeBase` に閉じている**点。案件 ORM を同一 DB に載せるには、**同一 `Base` 上にモデル定義を登録し、`init_db()` 実行前にメタデータにテーブルが載るよう import する**（または共有 `Base` を切り出す）必要がある。設計書の「composition root は原則変更しない」と **ルータマウント・スキーマ登録では最小限の既存ファイル変更が避けられない**ことの整理が実装前に有用。
- **API 層**は `APIRouter(prefix=..., tags=...)`、`Depends(get_db)`、サービス＋`SqlAlchemy*Repository` のパターンが `presentation/routers/talents.py` と `presentation/deps.py` に確立済み。**案件用は新パッケージ内に同型を複製**し、`get_session_factory` / `database_url` を既存 `infrastructure.persistence.database` から再利用するのが最短（共通 `get_db` をどこに置くかは軽い設計判断）。
- **Web**は `App.tsx`・`paths.ts`・`apiJson`・ページ分割の実例が揃っており、案件は **新ルート＋新ページ＋ナビ 1 行**で足せる。E2E は必須ではないが、既存 `e2e/happy-path.spec.ts` と同じ `webServer` で拡張可能。
- **推奨アプローチ**: 新パッケージ（設計どおり `project_registration`）＋既存 `main.py` / `schema.py` への**最小接続（Hybrid）**。工数は **S〜M（数日）**、リスクは **Low〜Medium**（Base／import 順の取り違えのみ注意）。

---

## 2. 現状調査（コードベース）

### 2.1 レイヤとエントリ

| 領域 | 状況 |
|------|------|
| FastAPI エントリ | `talent_interview_profile_poc/main.py` が単一 `app`。`include_router` で `/talents` 等のみ。`/cases` なし。 |
| DB 初期化 | `infrastructure/persistence/schema.py` の `init_db()` が `orm_models.Base.metadata.create_all` のみ。 |
| ORM の Base | `orm_models.py` 内の `class Base(DeclarativeBase)` が全テーブルの親。 |
| DI | `presentation/deps.py` の `get_db` と各 `get_*_service`。Session は `get_session_factory()` 由来。 |
| Web | `apps/web/src` に人材・テンプレ・デモ。案件ナビ・ページなし。 |

### 2.2 パッケージング

- `apps/api/pyproject.toml` は `[tool.setuptools.packages.find] where = ["src"]` のため、`src/project_registration/` を置けば**同一ディストリビューションに複数トップレベルパッケージ**として取り込まれる想定（`talent-interview-profile-poc` という配布名のまま二パッケージ共存）。
- `package-data` は人材パッケージのみ。案件側に YAML 同梱等がなければ追記不要。

### 2.3 既存仕様との境界

- `talent-interview-profile-poc` のルータ群と URL は独立。**`/cases` は衝突しない**。
- 要件の「既存 API・画面を本リリースで変更しない」は、**人材フローのロジックを改変しない**ことに留意すれば満たしやすい（`main.py` に数行追加する程度は「追加」と解釈可能）。

---

## 3. 要件ごとの充足度（Requirement-to-Asset）

| 要件 | 観点 | 状態 | メモ |
|------|------|------|------|
| 1 登録 | REST + 永続化 + 検証 | **Missing** | 新エンドポイント・ORM・サービス |
| 2 一覧・詳細 | GET 複数 | **Missing** | 同上 |
| 3 更新 | PATCH | **Missing** | 同上 |
| 4 最小 Web | 画面・ルート | **Missing** | `paths` / `App.tsx` / ページ |
| 5 対象外 | マッチング等 | **Constraint** | 新規で該当ルートを作らなければ満たす |

---

## 4. 実装アプローチ候補

### Option A: 既有人材パッケージへ直接追加

- **内容**: `talent_interview_profile_poc` 配下に `cases` ルータ・ORM・サービスを丸ごと入れる。
- **Pros**: `Base` / `init_db` / `deps` との一体化で import が単純。
- **Cons**: パッケージ肥大・境界が要件の「独立境界」とズレる。**非推奨**（設計書のパッケージ分割方針とも不一致）。

### Option B: 新パッケージ `project_registration`（設計どおり）

- **内容**: 新ディレクトリに 4 層を構築。`main.py` で `include_router`。ORM は **既存 `Base` を継承**するモジュールを `project_registration` 側に定義し、`schema.init_db` の前に **副作用 import** でメタデータ登録。
- **Pros**: 責務分離・テスト境界が明確。タスク `tasks.md` と一致。
- **Cons**: `project_registration` → `talent_interview_profile_poc.infrastructure.persistence.orm_models.Base` への依存が 1 本発生（PoC では許容、長期は共有 Base への抽出を Research に残す）。

### Option C: Hybrid（推奨の言い方）

- Option B に加え、**共有が避けられない箇所だけ**既存を触る：`main.py`（ルータ）、`schema.py`（モデル import）、必要なら `database.py` は無変更。
- フェーズ 2 で `shared` モジュールに `Base` / `get_db` を移す余地を残す。

---

## 5. 工数・リスク

| 項目 | 評価 | 理由 |
|------|------|------|
| Effort | **S〜M** | CRUD＋既存パターンの転記が主。Web も一覧・詳細・フォームの定番。 |
| Risk | **Low〜Medium** | `create_all` に新テーブルが載らないミス、循環 import、テーブル名 `cases` の予約語は SQLite では実害小。 |

---

## 6. Research Needed（設計・実装で確定すること）

1. **`Base` の所在**: 当面は人材パッケージの `Base` を継承するか、**薄い `shared.persistence` を新設して両パッケージから参照するか**（後者はタスク増・明確な長期整理）。
2. **`get_db` の所在**: 案件ルータが `Depends` で受け取る Generator を、`deps` 重複 vs talent の `get_db` 再エクスポート vs 共通モジュールのどれにするか（循環 import だけ避ける）。
3. **OpenAPI のアプリ名**: 単一アプリの `title` が人材向けのままになるギャップ。ドキュメント上の見栄えを直すかは任意。
4. **E2E**: 案件ハッピーパスを `e2e/` に足すかはポリシー次第（要件上は必須ではない）。

---

## 7. 設計フェーズへの持ち込み推奨

- **推奨**: **Option C（新パッケージ＋`main` / `schema` の最小接続）** を実装計画の既定とし、`design.md` に **「案件 ORM は `talent_interview_profile_poc...orm_models.Base` を継承し、`schema.init_db` 前に `project_registration...orm_models` を import」** を 1 文追記すると実装時の手戻りが減る。
- **次コマンド（任意）**: 設計書を上記で微修正したうえで **`/kiro-impl project-registration-poc`**。gap 単体では `design.md` の全面再生成は不要。

---

## 8. 会話用サマリー（300 語以内）

案件登録はコードが未着手のためギャップは全面的だが、人材 PoC が示す **FastAPI ルータ + SQLAlchemy + サービス + deps + React ページ** の型に沿えば実装路径は明確。技術的な焦点は **単一 SQLite に新テーブルを載せるための DeclarativeBase の共有と `init_db` へのモデル登録**であり、ここだけ設計書に一言足すと安全。新パッケージ分割（Option B/C）を推奨し、既有人材パッケージへの丸ごと統合（Option A）は避ける。工数は数日規模、リスクは中程度以下。次は実装か、設計書の接続方針の追記のみでよい。
