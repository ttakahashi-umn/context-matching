import { useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { DemoHelpPage } from "./presentation/pages/DemoHelpPage";
import { TalentDetailPage } from "./presentation/pages/TalentDetailPage";
import { TalentsPage } from "./presentation/pages/TalentsPage";
import { TemplatesPage } from "./presentation/pages/TemplatesPage";
import { paths } from "./presentation/routes/paths";

type HealthResponse = { status: string };

const navStyle = ({ isActive }: { isActive: boolean }) => ({
  marginRight: "1rem",
  fontWeight: isActive ? 700 : 400,
  color: isActive ? "#0a58ca" : "#333",
});

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
    <main style={{ fontFamily: "system-ui", padding: "2rem", maxWidth: "960px" }}>
      <header style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ marginTop: 0 }}>Talent Interview Profile PoC</h1>
        <nav>
          <NavLink to={paths.home} end style={navStyle}>
            ホーム
          </NavLink>
          <NavLink to={paths.talents} style={navStyle}>
            人材
          </NavLink>
          <NavLink to={paths.templates} style={navStyle}>
            テンプレート
          </NavLink>
          <NavLink to={paths.demo} style={navStyle}>
            デモ手順
          </NavLink>
        </nav>
        <p style={{ color: "#555", fontSize: "0.9rem" }}>
          API プロキシ: <code>/api</code> → バックエンド
          {health && (
            <>
              {" "}
              · <code>/health</code>: <strong>{health.status}</strong>
            </>
          )}
          {error && (
            <>
              {" "}
              · <span style={{ color: "crimson" }}>API: {error}</span>
            </>
          )}
        </p>
      </header>

      <Routes>
        <Route
          path={paths.home}
          element={
            <section>
              <p>左のナビからフローを開始してください。</p>
            </section>
          }
        />
        <Route path={paths.talents} element={<TalentsPage />} />
        <Route path="/talents/:talentId" element={<TalentDetailPage />} />
        <Route path={paths.templates} element={<TemplatesPage />} />
        <Route path={paths.demo} element={<DemoHelpPage />} />
      </Routes>
    </main>
  );
}
