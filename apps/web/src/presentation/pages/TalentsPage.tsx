import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, apiJson } from "../../infrastructure/http/client";
import { RegisterSlideOver } from "../components/RegisterSlideOver";
import { paths } from "../routes/paths";

type Talent = {
  id: string;
  family_name: string;
  given_name: string;
  family_name_kana: string;
  given_name_kana: string;
  display_label: string;
  created_at: string;
};

const emptyForm = {
  family_name: "",
  given_name: "",
  family_name_kana: "",
  given_name_kana: "",
};

const btnPrimary = "rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700";
const btnSecondary = "rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50";

export function TalentsPage() {
  const [talents, setTalents] = useState<Talent[]>([]);
  const [panelOpen, setPanelOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setMessage(null);
    try {
      const rows = await apiJson<Talent[]>("/talents");
      setTalents(rows);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function openRegisterPanel() {
    setMessage(null);
    setForm(emptyForm);
    setPanelOpen(true);
  }

  async function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    setMessage(null);
    try {
      await apiJson<Talent>("/talents", { method: "POST", json: form });
      setForm(emptyForm);
      setPanelOpen(false);
      await load();
    } catch (e) {
      if (e instanceof ApiError && e.isUnprocessable()) {
        setMessage("入力を確認してください（422）。");
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  function field(
    key: keyof typeof form,
    label: string,
    placeholder: string,
    opts?: { className?: string },
  ) {
    return (
      <label className="block min-w-[8rem] flex-1">
        <span className="mb-0.5 block text-xs font-medium text-slate-600">{label}</span>
        <input
          value={form[key]}
          onChange={(ev) => setForm((f) => ({ ...f, [key]: ev.target.value }))}
          placeholder={placeholder}
          required
          className={
            opts?.className ??
            "w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
          }
        />
      </label>
    );
  }

  return (
    <section className="max-w-4xl">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-800">人材</h2>
        <button type="button" className={btnPrimary} onClick={openRegisterPanel}>
          人材を登録
        </button>
      </div>

      {message && !panelOpen && (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {message}
        </p>
      )}

      <ul className="divide-y divide-slate-200 rounded-md border border-slate-200">
        {talents.length === 0 ? (
          <li className="px-3 py-8 text-center text-sm text-slate-500">登録された人材はまだありません。</li>
        ) : (
          talents.map((t) => (
            <li
              key={t.id}
              className="flex flex-col gap-0.5 px-3 py-2.5 text-sm hover:bg-slate-50 sm:flex-row sm:items-baseline sm:gap-x-2"
            >
              <Link to={paths.talent(t.id)} className="font-medium text-sky-700 hover:underline">
                {t.display_label}
              </Link>
              <span className="text-xs text-slate-500">
                （{t.family_name_kana} {t.given_name_kana}）
              </span>
              <code className="text-xs text-slate-400 sm:ml-auto">{t.id}</code>
            </li>
          ))
        )}
      </ul>

      <RegisterSlideOver open={panelOpen} onClose={() => setPanelOpen(false)} title="人材を登録">
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="flex flex-wrap gap-3">
            {field("family_name", "姓", "山田")}
            {field("given_name", "名", "太郎")}
          </div>
          <div className="flex flex-wrap gap-3">
            {field("family_name_kana", "姓（よみ）", "やまだ")}
            {field("given_name_kana", "名（よみ）", "たろう")}
          </div>
          {message && (
            <p role="alert" className="text-sm text-red-600">
              {message}
            </p>
          )}
          <div className="flex flex-wrap gap-2 pt-2">
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
