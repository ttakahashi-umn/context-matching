import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiJson } from "../../infrastructure/http/client";
import { ReadableMergedProfile } from "../components/ReadableMergedProfile";
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
  "min-w-[16rem] rounded-md border border-slate-300 px-2 py-1.5 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500";

const transcriptExcerptMax = 200;

function excerptTranscript(text: string, maxLen: number): string {
  const singleLine = text.replace(/\s+/g, " ").trim();
  if (singleLine.length <= maxLen) {
    return singleLine;
  }
  return `${singleLine.slice(0, maxLen)}…`;
}

function formatRequestFailure(e: unknown): string {
  if (e instanceof ApiError) {
    const body = e.body;
    if (body && typeof body === "object" && "detail" in body) {
      const d = (body as { detail: unknown }).detail;
      if (typeof d === "string") {
        return `リクエストが正常に完了しませんでした（HTTP ${e.status}）。${d}`;
      }
      if (Array.isArray(d)) {
        return `リクエストが正常に完了しませんでした（HTTP ${e.status}）。入力内容を確認してください。`;
      }
    }
    return `リクエストが正常に完了しませんでした（HTTP ${e.status}）。`;
  }
  return e instanceof Error ? e.message : String(e);
}

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
  /** POST/GET 抽出の待ち時間中は画面操作を止める */
  const [extractionBusy, setExtractionBusy] = useState(false);

  const canExtract = useMemo(
    () => Boolean(selectedInterviewId && selectedTemplateId),
    [selectedInterviewId, selectedTemplateId],
  );

  const interviewsNewestFirst = useMemo(
    () => [...interviews].sort((a, b) => b.created_at.localeCompare(a.created_at)),
    [interviews],
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
    if (!talentId || extractionBusy) return;
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
      } else if (e instanceof ApiError) {
        setMessage(formatRequestFailure(e));
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  async function runExtraction() {
    if (!canExtract || extractionBusy) return;
    setExtractionBusy(true);
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
        if (guard > 120) {
          setMessage(
            "抽出結果の取得がタイムアウトしました。しばらくしてから再度「抽出実行」を試すか、サーバーログを確認してください。",
          );
          setLastRun(run);
          return;
        }
        await new Promise((r) => setTimeout(r, 150));
        run = await apiJson<ExtractionRun>(`/extractions/${runId}`);
      }
      setLastRun(run);
      if (run.status === "failed") {
        setMessage(
          `抽出は正常系で終了しませんでした（ステータス: failed）。${run.error_message ?? "理由の詳細はありません。"}`,
        );
      }
    } catch (e) {
      if (e instanceof ApiError && e.isConflict()) {
        setMessage("リクエストが正常に完了しませんでした（HTTP 409）。同一面談で抽出が実行中の可能性があります。完了後に再試行してください。");
      } else if (e instanceof ApiError) {
        setMessage(formatRequestFailure(e));
      } else {
        setMessage(`リクエストが正常に完了しませんでした。${e instanceof Error ? e.message : String(e)}`);
      }
    } finally {
      setExtractionBusy(false);
    }
  }

  async function mergeProfile() {
    if (extractionBusy) return;
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
      } else if (e instanceof ApiError) {
        setMessage(formatRequestFailure(e));
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  if (!talentId) {
    return <p className="text-sm text-slate-600">人材 ID がありません。</p>;
  }

  return (
    <section className="max-w-6xl">
      <p className={`mb-2 ${extractionBusy ? "pointer-events-none opacity-50" : ""}`}>
        <Link to={paths.talents} className="text-sm text-sky-700 hover:underline" tabIndex={extractionBusy ? -1 : undefined}>
          ← 人材一覧
        </Link>
      </p>

      {extractionBusy && (
        <p
          role="status"
          aria-live="polite"
          className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
        >
          抽出を実行しています。サーバーから応答が返るまでこの画面の操作はできません。
        </p>
      )}
      {message && (
        <p role="alert" className="mb-4 text-sm text-red-600">
          {message}
        </p>
      )}

      <div className="grid grid-cols-1 gap-8 pt-2 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-8 lg:pt-4">
        {/* 左: 人材識別・マージ済みプロフィール（50%） */}
        <div className="min-w-0 space-y-6">
          <header className="space-y-1 border-b border-slate-100 pb-4">
            <h2 className="text-lg font-semibold text-slate-800">{talent?.display_label ?? "読み込み中…"}</h2>
            {talent && (
              <p className="text-sm text-slate-600">
                よみ: {talent.family_name_kana} {talent.given_name_kana}
              </p>
            )}
            <p className="text-xs text-slate-500">
              ID: <code className="rounded bg-slate-100 px-1">{talentId}</code>
            </p>
            {talent && (
              <p className="text-xs text-slate-500">
                登録日時: <time dateTime={talent.created_at}>{talent.created_at}</time>
              </p>
            )}
          </header>

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">マージ済みプロフィール</h3>
            {talent?.latest_profile_json ? (
              <ReadableMergedProfile data={talent.latest_profile_json} />
            ) : (
              <p className="text-sm text-slate-500">まだ反映されていません。</p>
            )}
          </div>
        </div>

        {/* 右: 面談登録・抽出・面談履歴・反映履歴（50%） */}
        <div className="min-w-0 space-y-8">
          <div>
            <h3 id="talent-detail-interview-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
              面談テキストの登録
            </h3>
            <form onSubmit={addInterview} className="space-y-2">
              <textarea
                aria-labelledby="talent-detail-interview-heading"
                value={transcript}
                onChange={(ev) => setTranscript(ev.target.value)}
                rows={5}
                disabled={extractionBusy}
                className="w-full rounded-md border border-slate-300 p-3 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500"
              />
              <div>
                <button type="submit" disabled={extractionBusy} className={btnPrimary}>
                  面談を追加
                </button>
              </div>
            </form>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">抽出とプロフィール反映</h3>
            <div className="mb-3">
              <span id="talent-detail-interview-select-label" className={fieldLabel}>
                対象面談
              </span>
              <select
                aria-labelledby="talent-detail-interview-select-label"
                value={selectedInterviewId}
                onChange={(ev) => setSelectedInterviewId(ev.target.value)}
                disabled={extractionBusy}
                className={`${selectCls} mt-1 w-full max-w-full`}
              >
                {interviews.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.created_at} — {excerptTranscript(i.transcript_text, 72)}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-3">
              <span id="talent-detail-template-select-label" className={fieldLabel}>
                テンプレ
              </span>
              <select
                aria-labelledby="talent-detail-template-select-label"
                value={selectedTemplateId}
                onChange={(ev) => setSelectedTemplateId(ev.target.value)}
                disabled={extractionBusy}
                className={`${selectCls} mt-1 w-full max-w-full`}
              >
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.purpose} — {t.version_label}（{t.id}）
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={!canExtract || extractionBusy}
                className={btnPrimary}
                onClick={() => void runExtraction()}
              >
                {extractionBusy ? "抽出実行中…" : "抽出実行"}
              </button>
              <button type="button" disabled={extractionBusy} className={btnSecondary} onClick={() => void mergeProfile()}>
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
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">面談履歴</h3>
            {interviewsNewestFirst.length === 0 ? (
              <p className="text-sm text-slate-500">まだ面談がありません。上のフォームから登録できます。</p>
            ) : (
              <ul
                className="max-h-64 divide-y divide-slate-200 overflow-y-auto rounded-md border border-slate-200 text-sm"
                aria-label="登録済み面談セッション（新しい順）"
              >
                {interviewsNewestFirst.map((i) => {
                  const selected = i.id === selectedInterviewId;
                  return (
                    <li key={i.id}>
                      <button
                        type="button"
                        disabled={extractionBusy}
                        onClick={() => setSelectedInterviewId(i.id)}
                        className={`flex w-full flex-col gap-0.5 px-3 py-2.5 text-left transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 ${
                          selected ? "bg-sky-50 ring-1 ring-inset ring-sky-200" : ""
                        }`}
                      >
                        <span className="text-xs text-slate-500">
                          <time dateTime={i.created_at}>{i.created_at}</time>
                          <span className="ml-2 font-mono text-[11px] text-slate-400">{i.id}</span>
                          {selected ? (
                            <span className="ml-2 rounded bg-sky-200 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-sky-900">
                              抽出対象
                            </span>
                          ) : null}
                        </span>
                        <span className="line-clamp-3 text-slate-800">{excerptTranscript(i.transcript_text, transcriptExcerptMax)}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">プロフィール反映履歴</h3>
            <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 text-sm">
              {history.length === 0 ? (
                <li className="px-3 py-4 text-slate-500">まだ反映履歴がありません。</li>
              ) : (
                history.map((h) => (
                  <li key={h.id} className="px-3 py-2 hover:bg-slate-50">
                    <code className="text-xs">{h.id}</code> ← <code className="text-xs">{h.source_extraction_run_id}</code>
                    <span className="ml-2 text-xs text-slate-500">{h.created_at}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
