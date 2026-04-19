# talent-interview-profile-poc デモ手順

同一操作列で同じ観察結果に到達するための最小手順です。

1. API と Web を起動する（ルート `README.md` の手順）。
2. Web の「人材」で表示名を入力し「登録」する。
3. 登録した人材のリンクを開き、面談テキストを入力して「面談を追加」する。
4. 「テンプレート」で `examples/templates/default_template.yaml` と同等の YAML を登録する（未登録の場合）。
5. 人材詳細に戻り、テンプレを選んで「抽出実行」を押す。完了まで数秒以内（スタブ既定）。
6. 「プロフィール反映」を押し、マージ済みプロフィールと履歴にスナップショットが増えることを確認する。
7. 根拠として、画面上の `interview_session_id` / `extraction_run_id` / `template_version_id` を控える。
8. 任意: `GET /exports/talents/<talent_id>.json` でエクスポート JSON を取得する。
