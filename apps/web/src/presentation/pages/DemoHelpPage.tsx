import { Link } from "react-router-dom";
import { paths } from "../routes/paths";

export function DemoHelpPage() {
  return (
    <section>
      <h2>デモ手順</h2>
      <ol style={{ lineHeight: 1.6 }}>
        <li>
          <Link to={paths.talents}>人材一覧</Link>で人材を作成する。
        </li>
        <li>人材詳細で面談テキストを投入する。</li>
        <li>
          <Link to={paths.templates}>テンプレート</Link>で YAML を登録する（未登録なら）。
        </li>
        <li>詳細画面でテンプレを選び「抽出実行」→ 完了後「プロフィール反映」。</li>
        <li>
          根拠確認: 画面に表示される <code>interview_session_id</code> / <code>extraction_run_id</code> /{" "}
          <code>template_version_id</code> をメモする。
        </li>
      </ol>
      <p>
        API の JSON エクスポート: <code>GET /exports/talents/&lt;id&gt;.json</code>（プロキシ経由は{" "}
        <code>/api/exports/talents/&lt;id&gt;.json</code>）。
      </p>
    </section>
  );
}
