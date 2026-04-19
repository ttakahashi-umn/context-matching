import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, apiJson } from "../../infrastructure/http/client";
import { paths } from "../routes/paths";

type Talent = {
  id: string;
  display_name: string;
  created_at: string;
};

export function TalentsPage() {
  const [talents, setTalents] = useState<Talent[]>([]);
  const [name, setName] = useState("");
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

  async function onSubmit(ev: FormEvent) {
    ev.preventDefault();
    setMessage(null);
    try {
      await apiJson<Talent>("/talents", { method: "POST", json: { display_name: name } });
      setName("");
      await load();
    } catch (e) {
      if (e instanceof ApiError && e.isUnprocessable()) {
        setMessage("入力を確認してください（422）。");
      } else {
        setMessage(e instanceof Error ? e.message : String(e));
      }
    }
  }

  return (
    <section>
      <h2>人材一覧</h2>
      <form onSubmit={onSubmit} style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <input
          value={name}
          onChange={(ev) => setName(ev.target.value)}
          placeholder="表示名"
          required
          style={{ flex: 1, maxWidth: "20rem" }}
        />
        <button type="submit">登録</button>
      </form>
      {message && (
        <p role="alert" style={{ color: "crimson" }}>
          {message}
        </p>
      )}
      <ul>
        {talents.map((t) => (
          <li key={t.id}>
            <Link to={paths.talent(t.id)}>{t.display_name}</Link>
            <span style={{ color: "#666", marginLeft: "0.5rem" }}>
              <code>{t.id}</code>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
