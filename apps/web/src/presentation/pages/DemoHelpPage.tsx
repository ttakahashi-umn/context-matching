import { Link } from "react-router-dom";
import { paths } from "../routes/paths";

export function DemoHelpPage() {
  return (
    <section className="max-w-2xl text-sm text-slate-600">
      <h2 className="mb-4 text-base font-medium text-slate-700">デモ手順</h2>
      <ol className="list-decimal space-y-2 pl-5 leading-relaxed">
        <li>
          <Link to={paths.talents} className="text-sky-700 hover:underline">
            人材
          </Link>
          で「人材を登録」から右パネルを開き、フォームで登録する。
        </li>
        <li>人材詳細で面談テキストを投入する。</li>
        <li>
          <Link to={paths.templates} className="text-sky-700 hover:underline">
            テンプレート
          </Link>
          で「テンプレートを登録」から右パネルを開き、YAML を登録する（未登録なら）。
        </li>
        <li>詳細でテンプレを選び「抽出実行」→ 完了後「プロフィール反映」。</li>
        <li>
          根拠: 画面上の <code className="rounded bg-slate-100 px-1 text-xs">interview_session_id</code> /{" "}
          <code className="rounded bg-slate-100 px-1 text-xs">extraction_run_id</code> /{" "}
          <code className="rounded bg-slate-100 px-1 text-xs">template_version_id</code>
        </li>
      </ol>
      <p className="mt-4 text-xs text-slate-500">
        JSON エクスポート: <code className="rounded bg-slate-100 px-1">GET /exports/talents/&lt;id&gt;.json</code>（
        <code className="rounded bg-slate-100 px-1">/api/exports/…</code>）
      </p>
    </section>
  );
}
