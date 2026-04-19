import { useEffect, useState } from "react";

type HealthResponse = { status: string };

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetch("/api/health");
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const body = (await res.json()) as HealthResponse;
        if (!cancelled) {
          setHealth(body);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e));
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>Talent Interview Profile PoC</h1>
      <p>API プロキシ: <code>/api</code> → バックエンド</p>
      {health && (
        <p>
          <code>/health</code>: <strong>{health.status}</strong>
        </p>
      )}
      {error && (
        <p role="alert" style={{ color: "crimson" }}>
          API 接続エラー: {error}
        </p>
      )}
    </main>
  );
}
