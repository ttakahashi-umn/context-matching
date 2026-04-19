import { FormEvent, useCallback, useEffect, useState } from "react";
import { ApiError, apiJson } from "../../infrastructure/http/client";
import { RegisterSlideOver } from "../components/RegisterSlideOver";

type TemplateRow = {
  id: string;
  version_label: string;
  purpose: string;
  yaml_text: string;
  created_at: string;
};

const defaultYaml = `version: "1.0.0-poc"
purpose: "PoC 用の最小テンプレ"
fields:
  summary: string
`;

const btnPrimary = "rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700";
const btnSecondary = "rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50";

export function TemplatesPage() {
  const [rows, setRows] = useState<TemplateRow[]>([]);
  const [panelOpen, setPanelOpen] = useState(false);
  const [yaml, setYaml] = useState(defaultYaml);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setMessage(null);
    try {
      const list = await apiJson<TemplateRow[]>("/templates");
      setRows(list);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function openRegisterPanel() {
    setMessage(null);
    setYaml(defaultYaml);
    setPanelOpen(true);
  }

  async function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    setMessage(null);
    try {
      await apiJson<{ template_version_id: string; semver: string }>("/templates", {
        method: "POST",
        json: { yaml_text: yaml },
      });
      setYaml(defaultYaml);
      setPanelOpen(false);
      await load();
    } catch (e) {
      if (e instanceof ApiError && e.isUnprocessable()) {
        setMessage("YAML が不正です（422）。修正して再試行してください。");
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  return (
    <section className="max-w-4xl">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-800">テンプレート</h2>
        <button type="button" className={btnPrimary} onClick={openRegisterPanel}>
          テンプレートを登録
        </button>
      </div>

      {message && !panelOpen && (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {message}
        </p>
      )}

      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">登録済み</h3>
      <ul className="divide-y divide-slate-200 rounded-md border border-slate-200">
        {rows.length === 0 ? (
          <li className="px-3 py-8 text-center text-sm text-slate-500">登録されたテンプレートはまだありません。</li>
        ) : (
          rows.map((r) => (
            <li key={r.id} className="px-3 py-2 text-sm hover:bg-slate-50">
              <div className="font-medium text-slate-800">{r.version_label}</div>
              <div className="text-slate-600">用途: {r.purpose}</div>
              <code className="text-xs text-slate-500">{r.id}</code>
            </li>
          ))
        )}
      </ul>

      <RegisterSlideOver
        open={panelOpen}
        onClose={() => setPanelOpen(false)}
        title="テンプレートを登録"
        panelMaxWidthClass="max-w-2xl"
      >
        <form onSubmit={onSubmit} className="space-y-3">
          <p className="text-xs text-slate-500">ルートに version・purpose など必須項目を含む YAML を貼り付けてください。</p>
          <textarea
            aria-label="テンプレート YAML"
            value={yaml}
            onChange={(ev) => setYaml(ev.target.value)}
            rows={16}
            className="min-h-[12rem] w-full rounded-md border border-slate-300 p-3 font-mono text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
          {message && (
            <p role="alert" className="text-sm text-red-600">
              {message}
            </p>
          )}
          <div className="flex flex-wrap gap-2 pt-1">
            <button type="submit" className={btnPrimary}>
              登録
            </button>
            <button type="button" className={btnSecondary} onClick={() => setPanelOpen(false)}>
              キャンセル
            </button>
          </div>
        </form>
      </RegisterSlideOver>
    </section>
  );
}
