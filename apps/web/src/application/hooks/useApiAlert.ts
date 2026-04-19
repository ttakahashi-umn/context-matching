import { useCallback, useState } from "react";
import { ApiError } from "../../infrastructure/http/client";

/** 422 / 409 を人間向け短文に落とす（画面用） */
export function useApiAlert() {
  const [message, setMessage] = useState<string | null>(null);

  const clear = useCallback(() => setMessage(null), []);

  const setFromError = useCallback((err: unknown) => {
    if (err instanceof ApiError) {
      if (err.isConflict()) {
        setMessage("競合が発生しました（409）。しばらく待って再試行してください。");
        return;
      }
      if (err.isUnprocessable()) {
        setMessage("入力内容を確認してください（422）。");
        return;
      }
    }
    setMessage(err instanceof Error ? err.message : String(err));
  }, []);

  return { message, setMessage, clear, setFromError };
}
