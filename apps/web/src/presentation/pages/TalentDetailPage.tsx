import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiJson } from "../../infrastructure/http/client";
import { paths } from "../routes/paths";

type Talent = {
  id: string;
  display_name: string;
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
    return <p>人材 ID がありません。</p>;
  }

  return (
    <section>
      <p>
        <Link to={paths.talents}>← 一覧へ</Link>
      </p>
      <h2>{talent?.display_name ?? "読み込み中…"}</h2>
      <p>
        人材 ID: <code>{talentId}</code>
      </p>
      {message && (
        <p role="alert" style={{ color: "crimson" }}>
          {message}
        </p>
      )}

      <h3>面談</h3>
      <form onSubmit={addInterview} style={{ marginBottom: "1rem" }}>
        <textarea
          value={transcript}
          onChange={(ev) => setTranscript(ev.target.value)}
          rows={5}
          style={{ width: "100%", maxWidth: "40rem" }}
        />
        <div style={{ marginTop: "0.5rem" }}>
          <button type="submit">面談を追加</button>
        </div>
      </form>
      <label>
        対象面談:{" "}
        <select
          value={selectedInterviewId}
          onChange={(ev) => setSelectedInterviewId(ev.target.value)}
          style={{ minWidth: "16rem" }}
        >
          {interviews.map((i) => (
            <option key={i.id} value={i.id}>
              {i.id}（{i.created_at}）
            </option>
          ))}
        </select>
      </label>

      <h3 style={{ marginTop: "1.5rem" }}>抽出</h3>
      <label>
        テンプレ:{" "}
        <select
          value={selectedTemplateId}
          onChange={(ev) => setSelectedTemplateId(ev.target.value)}
          style={{ minWidth: "16rem" }}
        >
          {templates.map((t) => (
            <option key={t.id} value={t.id}>
              {t.version_label}（{t.id}）
            </option>
          ))}
        </select>
      </label>
      <div style={{ marginTop: "0.5rem" }}>
        <button type="button" disabled={!canExtract} onClick={() => void runExtraction()}>
          抽出実行
        </button>
        <button type="button" style={{ marginLeft: "0.5rem" }} onClick={() => void mergeProfile()}>
          プロフィール反映
        </button>
      </div>
      {lastRun && (
        <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#f6f6f6" }}>
          <div>
            直近の抽出: <code>{lastRun.id}</code> / 状態 <strong>{lastRun.status}</strong>
          </div>
          <div>
            template_version_id: <code>{lastRun.template_version_id}</code>
          </div>
          <div>
            interview_session_id: <code>{lastRun.interview_session_id}</code>
          </div>
          <div>
            input_hash: <code>{lastRun.input_hash}</code>
          </div>
          {lastRun.result_json && (
            <pre style={{ marginTop: "0.5rem", fontSize: "0.85rem" }}>
              {JSON.stringify(lastRun.result_json, null, 2)}
            </pre>
          )}
        </div>
      )}

      <h3 style={{ marginTop: "1.5rem" }}>マージ済みプロフィール</h3>
      {talent?.latest_profile_json ? (
        <pre style={{ background: "#f6f6f6", padding: "0.75rem" }}>
          {JSON.stringify(talent.latest_profile_json, null, 2)}
        </pre>
      ) : (
        <p>まだ反映されていません。</p>
      )}

      <h3 style={{ marginTop: "1.5rem" }}>反映履歴</h3>
      <ul>
        {history.map((h) => (
          <li key={h.id}>
            <code>{h.id}</code> ← extraction <code>{h.source_extraction_run_id}</code>（{h.created_at}）
          </li>
        ))}
      </ul>
    </section>
  );
}
