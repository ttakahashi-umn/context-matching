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

type PanelMode = "register" | "edit";

const defaultYaml = `version: "1.0.0-poc"
purpose: "PoC 用の最小テンプレ"
fields:
  summary: string
`;

const btnPrimary = "rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700";
const btnSecondary = "rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50";
const btnLink = "text-sm font-medium text-sky-700 hover:underline";

export function TemplatesPage() {
  const [rows, setRows] = useState<TemplateRow[]>([]);
  const [panelOpen, setPanelOpen] = useState(false);
  const [panelMode, setPanelMode] = useState<PanelMode>("register");
  const [editingId, setEditingId] = useState<string | null>(null);
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

  function closePanel() {
    setPanelOpen(false);
    setEditingId(null);
    setMessage(null);
  }

  function openRegisterPanel() {
    setPanelMode("register");
    setEditingId(null);
    setYaml(defaultYaml);
    setMessage(null);
    setPanelOpen(true);
  }

  function openEditPanel(row: TemplateRow) {
    setPanelMode("edit");
    setEditingId(row.id);
    setYaml(row.yaml_text);
    setMessage(null);
    setPanelOpen(true);
  }

  async function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    setMessage(null);
    try {
      if (panelMode === "edit" && editingId) {
        await apiJson<TemplateRow>(`/templates/${editingId}`, {
          method: "PATCH",
          json: { yaml_text: yaml },
        });
      } else {
        await apiJson<{ template_version_id: string; semver: string }>("/templates", {
          method: "POST",
          json: { yaml_text: yaml },
        });
      }
      setYaml(defaultYaml);
      closePanel();
      await load();
    } catch (e) {
      if (e instanceof ApiError && e.isUnprocessable()) {
        setMessage("YAML が不正です（422）。修正して再試行してください。");
      } else if (e instanceof ApiError && e.isConflict()) {
        setMessage(
          "version（ラベル）が別のテンプレートと重複しています（409）。YAML の version を変えるか、他方を先に変更してください。",
        );
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  const panelTitle = panelMode === "edit" ? "テンプレートを確認・編集" : "テンプレートを登録";
  const submitLabel = panelMode === "edit" ? "保存" : "登録";

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
            <li key={r.id} className="flex flex-col gap-1 px-3 py-2 text-sm hover:bg-slate-50 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="font-medium text-slate-800">{r.version_label}</div>
                <div className="text-slate-600">用途: {r.purpose}</div>
                <code className="text-xs text-slate-500">{r.id}</code>
              </div>
              <button type="button" className={`${btnLink} shrink-0 self-start`} onClick={() => openEditPanel(r)}>
                確認・編集
              </button>
            </li>
          ))
        )}
      </ul>

      <RegisterSlideOver open={panelOpen} onClose={closePanel} title={panelTitle} panelMaxWidthClass="max-w-2xl">
        <form onSubmit={onSubmit} className="space-y-3">
          <p className="text-xs text-slate-500">
            ルートに version・purpose など必須項目を含む YAML を編集できます。保存すると当該テンプレート行が置き換わります（同一
            UUID）。
          </p>
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
              {submitLabel}
            </button>
            <button type="button" className={btnSecondary} onClick={closePanel}>
              キャンセル
            </button>
          </div>
        </form>
      </RegisterSlideOver>
    </section>
  );
}
