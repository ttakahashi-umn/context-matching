# Implementation Plan: project-registration-poc

## 実装タスク

- [ ] 1. パッケージ骨格と設定
- [ ] 1.1 `apps/api/src/project_registration/` のレイヤーディレクトリ作成と空ルータのエクスポート (P)
  - `presentation` / `application` / `domain` / `infrastructure` が存在し、パッケージが import 可能である。
  - _Requirements: 1（間接）_
  - _Boundary: apps/api 新パッケージ_
- [ ] 1.2 composition root で案件ルータをマウント（プレフィクス `/cases`）
  - 既存人材 PoC の `/health` 等が壊れず、新パスが OpenAPI に現れる。
  - _Requirements: 1, 2_
  - _Boundary: talent_interview_profile_poc.main または同等の組み立て_
  - _Depends: 1.1_

- [ ] 2. ドメインと永続化
- [ ] 2.1 案件エンティティ・ドメイン例外・リポジトリ抽象の定義 (P)
  - Case エンティティと status 列挙、リポジトリ Protocol が要件の操作意図を列挙している。
  - _Requirements: 1, 2, 3_
  - _Boundary: domain_
- [ ] 2.2 ORM モデル・テーブル `cases`（名称は実装で確定）とリポジトリ具象
  - 空 DB にスキーマ展開され、作成・取得・一覧・更新が往復する。
  - _Requirements: 1, 2, 3_
  - _Boundary: infrastructure persistence_
  - _Depends: 2.1_

- [ ] 3. アプリケーションと HTTP
- [ ] 3.1 案件ユースケースサービス（登録・一覧・取得・更新）
  - 検証失敗・存在しない ID が判別可能な失敗になる。
  - _Requirements: 1, 2, 3_
  - _Boundary: application_
  - _Depends: 2.2_
- [ ] 3.2 案件ルーター・Pydantic DTO・ステータスコード整形
  - POST 201、GET 一覧・詳細、PATCH、404/422 の一貫性。
  - _Requirements: 1, 2, 3_
  - _Boundary: presentation routers, schemas_
  - _Depends: 3.1, 1.2_

- [ ] 4. Web
- [ ] 4.1 ルート・HTTP クライアント拡張（`/cases`）
  - 基底 URL と既存 fetch ラッパで 422/404 が判別可能。
  - _Requirements: 4_
  - _Boundary: apps/web infrastructure http, routes_
- [ ] 4.2 案件一覧・登録・詳細（編集）画面
  - 画面のみで登録・一覧・開く・保存が完遂できる。
  - _Requirements: 4_
  - _Boundary: apps/web presentation pages_
  - _Depends: 4.1, 3.2_

- [ ] 5. 検証と仕上げ
- [ ] 5.1 API 自動テスト（サービス + ルータ結合）
  - 必須欠落・存在しない ID・正常系の登録→取得→更新が赤緑で守られる。
  - _Requirements: 1, 2, 3_
  - _Boundary: tests_
  - _Depends: 3.2_
- [ ] 5.2 対象外パスの非提供確認（マッチング等）
  - 誤ってマッチング API を追加していない（または明示的に対象外）。
  - _Requirements: 5_
  - _Boundary: presentation_
  - _Depends: 3.2_
- [ ] 5.3 ルート README または `docs/` に案件 API・画面の起動手順を追記
  - 新規開発者が `make api-dev` / `make web-dev` で案件まで到達できる。
  - _Requirements: 4_
  - _Depends: 4.2_
  - _Optional: Makefile に `cases` 向けの目印コメントのみ（必須ではない）_

## Implementation Notes

- （実装時に記載）
