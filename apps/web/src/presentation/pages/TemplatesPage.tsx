import { FormEvent, useCallback, useEffect, useState } from "react";
import { ApiError, apiJson } from "../../infrastructure/http/client";

type TemplateRow = {
  id: string;
  version_label: string;
  yaml_text: string;
  created_at: string;
};

export function TemplatesPage() {
  const [rows, setRows] = useState<TemplateRow[]>([]);
  const [yaml, setYaml] = useState(`version: "1.0.0-poc"\nfields:\n  summary: string\n`);
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

  async function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    setMessage(null);
    try {
      await apiJson<{ template_version_id: string; semver: string }>("/templates", {
        method: "POST",
        json: { yaml_text: yaml },
      });
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
    <section>
      <h2>テンプレート</h2>
      <form onSubmit={onSubmit}>
        <textarea
          value={yaml}
          onChange={(ev) => setYaml(ev.target.value)}
          rows={12}
          style={{ width: "100%", maxWidth: "40rem", fontFamily: "monospace" }}
        />
        <div style={{ marginTop: "0.5rem" }}>
          <button type="submit">登録</button>
        </div>
      </form>
      {message && (
        <p role="alert" style={{ color: "crimson" }}>
          {message}
        </p>
      )}
      <h3 style={{ marginTop: "1.5rem" }}>登録済み</h3>
      <ul>
        {rows.map((r) => (
          <li key={r.id}>
            <strong>{r.version_label}</strong> <code>{r.id}</code>
          </li>
        ))}
      </ul>
    </section>
  );
}
