import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiJson } from "../../infrastructure/http/client";
import { paths } from "../routes/paths";

type Talent = {
  id: string;
  family_name: string;
  given_name: string;
  family_name_kana: string;
  given_name_kana: string;
  display_label: string;
  created_at: string;
  latest_profile_json: Record<string, unknown> | null;
};

type Interview = {
  id: string;
  talent_id: string;
  transcript_text: string;
  created_at: string;
};

type TemplateRow = {
  id: string;
  version_label: string;
  purpose: string;
  yaml_text: string;
  created_at: string;
};

type ExtractionRun = {
  id: string;
  interview_session_id: string;
  template_version_id: string;
  status: string;
  result_json: Record<string, unknown> | null;
  error_message: string | null;
  input_hash: string;
  model_id: string | null;
  prompt_fingerprint: string | null;
  created_at: string;
};

type ProfileSnapshot = {
  id: string;
  talent_id: string;
  merged_profile_json: Record<string, unknown>;
  source_extraction_run_id: string;
  created_at: string;
};

const btnPrimary =
  "rounded-md bg-slate-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50";
const btnSecondary =
  "rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-800 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50";
const fieldLabel = "mb-1 block text-xs font-medium text-slate-600";
const selectCls =
  "min-w-[16rem] rounded-md border border-slate-300 px-2 py-1.5 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500";

export function TalentDetailPage() {
  const { talentId = "" } = useParams();
  const [talent, setTalent] = useState<Talent | null>(null);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [templates, setTemplates] = useState<TemplateRow[]>([]);
  const [transcript, setTranscript] = useState("面談メモ: チーム開発と設計について話した。");
  const [selectedInterviewId, setSelectedInterviewId] = useState<string>("");
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");
  const [lastRun, setLastRun] = useState<ExtractionRun | null>(null);
  const [history, setHistory] = useState<ProfileSnapshot[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  const canExtract = useMemo(
    () => Boolean(selectedInterviewId && selectedTemplateId),
    [selectedInterviewId, selectedTemplateId],
  );

  const loadTalent = useCallback(async () => {
    if (!talentId) return;
    const t = await apiJson<Talent>(`/talents/${talentId}`);
    setTalent(t);
  }, [talentId]);

  const loadInterviews = useCallback(async () => {
    if (!talentId) return;
    const rows = await apiJson<Interview[]>(`/talents/${talentId}/interviews`);
    setInterviews(rows);
  }, [talentId]);

  const loadTemplates = useCallback(async () => {
    const rows = await apiJson<TemplateRow[]>("/templates");
    setTemplates(rows);
  }, []);

  const loadHistory = useCallback(async () => {
    if (!talentId) return;
    const rows = await apiJson<ProfileSnapshot[]>(`/talents/${talentId}/profile/history`);
    setHistory(rows);
  }, [talentId]);

  const refreshAll = useCallback(async () => {
    setMessage(null);
    try {
      await loadTalent();
      await loadInterviews();
      await loadTemplates();
      await loadHistory();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    }
  }, [loadHistory, loadInterviews, loadTalent, loadTemplates]);

  useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  useEffect(() => {
    if (interviews.length === 0) {
      return;
    }
    setSelectedInterviewId((prev) => prev || (interviews[interviews.length - 1]?.id ?? ""));
  }, [interviews]);

  useEffect(() => {
    if (templates.length === 0) {
      return;
    }
    setSelectedTemplateId((prev) => prev || (templates[0]?.id ?? ""));
  }, [templates]);

  async function addInterview(ev: FormEvent) {
    ev.preventDefault();
    if (!talentId) return;
    setMessage(null);
    try {
      const res = await apiJson<{ interview_session_id: string }>(`/talents/${talentId}/interviews`, {
        method: "POST",
        json: { transcript_text: transcript },
      });
      setSelectedInterviewId(res.interview_session_id);
      await loadInterviews();
      await loadTalent();
    } catch (e) {
      if (e instanceof ApiError && e.isUnprocessable()) {
        setMessage("面談テキストが不正、またはサイズ上限超過です（422）。");
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  async function runExtraction() {
    setMessage(null);
    try {
      const started = await apiJson<{ extraction_run_id: string; status: string }>("/extractions", {
        method: "POST",
        json: {
          interview_session_id: selectedInterviewId,
          template_version_id: selectedTemplateId,
        },
      });
      const runId = started.extraction_run_id;
      let run = await apiJson<ExtractionRun>(`/extractions/${runId}`);
      let guard = 0;
      while (run.status === "running" || run.status === "pending") {
        guard += 1;
        if (guard > 50) break;
        await new Promise((r) => setTimeout(r, 50));
        run = await apiJson<ExtractionRun>(`/extractions/${runId}`);
      }
      setLastRun(run);
      if (run.status === "failed") {
        setMessage(run.error_message ?? "抽出に失敗しました。");
      }
    } catch (e) {
      if (e instanceof ApiError && e.isConflict()) {
        setMessage("同一面談で抽出が実行中です（409）。完了後に再試行してください。");
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  async function mergeProfile() {
    if (!talentId || !lastRun || lastRun.status !== "completed") {
      setMessage("完了した抽出がありません。");
      return;
    }
    setMessage(null);
    try {
      await apiJson("/profiles/merge", {
        method: "POST",
        json: { talent_id: talentId, extraction_run_id: lastRun.id },
      });
      await loadTalent();
      await loadHistory();
    } catch (e) {
      if (e instanceof ApiError && e.isUnprocessable()) {
        setMessage("反映内容が拒否されました（422）。");
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  if (!talentId) {
    return <p className="text-sm text-slate-600">人材 ID がありません。</p>;
  }

  return (
    <section className="max-w-3xl">
      <p className="mb-4">
        <Link to={paths.talents} className="text-sm text-sky-700 hover:underline">
          ← 人材一覧
        </Link>
      </p>
      <h2 className="text-lg font-semibold text-slate-800">{talent?.display_label ?? "読み込み中…"}</h2>
      {talent && (
        <p className="mt-0.5 text-sm text-slate-600">
          よみ: {talent.family_name_kana} {talent.given_name_kana}
        </p>
      )}
      <p className="mt-1 text-xs text-slate-500">
        ID: <code className="rounded bg-slate-100 px-1">{talentId}</code>
      </p>
      {message && (
        <p role="alert" className="mt-3 text-sm text-red-600">
          {message}
        </p>
      )}

      <h3 className="mb-2 mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">面談</h3>
      <form onSubmit={addInterview} className="mb-4 space-y-2">
        <textarea
          value={transcript}
          onChange={(ev) => setTranscript(ev.target.value)}
          rows={5}
          className="w-full max-w-2xl rounded-md border border-slate-300 p-3 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
        />
        <div>
          <button type="submit" className={btnPrimary}>
            面談を追加
          </button>
        </div>
      </form>
      <div className="mb-6">
        <span className={fieldLabel}>対象面談</span>
        <select
          value={selectedInterviewId}
          onChange={(ev) => setSelectedInterviewId(ev.target.value)}
          className={selectCls}
        >
          {interviews.map((i) => (
            <option key={i.id} value={i.id}>
              {i.id}（{i.created_at}）
            </option>
          ))}
        </select>
      </div>

      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">抽出</h3>
      <div className="mb-2">
        <span className={fieldLabel}>テンプレ</span>
        <select
          value={selectedTemplateId}
          onChange={(ev) => setSelectedTemplateId(ev.target.value)}
          className={selectCls}
        >
          {templates.map((t) => (
            <option key={t.id} value={t.id}>
              {t.purpose} — {t.version_label}（{t.id}）
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-wrap gap-2">
        <button type="button" disabled={!canExtract} className={btnPrimary} onClick={() => void runExtraction()}>
          抽出実行
        </button>
        <button type="button" className={btnSecondary} onClick={() => void mergeProfile()}>
          プロフィール反映
        </button>
      </div>
      {lastRun && (
        <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm">
          <div>
            直近の抽出: <code className="text-xs">{lastRun.id}</code> /{" "}
            <span className="font-medium">{lastRun.status}</span>
          </div>
          <div className="mt-1 text-xs text-slate-600">
            template_version_id: <code>{lastRun.template_version_id}</code>
          </div>
          <div className="text-xs text-slate-600">
            interview_session_id: <code>{lastRun.interview_session_id}</code>
          </div>
          <div className="text-xs text-slate-600">
            input_hash: <code>{lastRun.input_hash}</code>
          </div>
          {lastRun.result_json && (
            <pre className="mt-2 max-h-64 overflow-auto rounded bg-white p-2 font-mono text-xs text-slate-800 ring-1 ring-slate-200">
              {JSON.stringify(lastRun.result_json, null, 2)}
            </pre>
          )}
        </div>
      )}

      <h3 className="mb-2 mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">マージ済みプロフィール</h3>
      {talent?.latest_profile_json ? (
        <pre className="max-h-80 overflow-auto rounded-md border border-slate-200 bg-slate-50 p-3 font-mono text-xs text-slate-800">
          {JSON.stringify(talent.latest_profile_json, null, 2)}
        </pre>
      ) : (
        <p className="text-sm text-slate-500">まだ反映されていません。</p>
      )}

      <h3 className="mb-2 mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">反映履歴</h3>
      <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 text-sm">
        {history.map((h) => (
          <li key={h.id} className="px-3 py-2 hover:bg-slate-50">
            <code className="text-xs">{h.id}</code> ← <code className="text-xs">{h.source_extraction_run_id}</code>
            <span className="ml-2 text-xs text-slate-500">{h.created_at}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
