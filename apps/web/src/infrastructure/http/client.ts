/** API 基底 URL（Vite では `/api` プロキシが既定） */
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, body: unknown, message?: string) {
    super(message ?? `HTTP ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }

  isConflict(): boolean {
    return this.status === 409;
  }

  isUnprocessable(): boolean {
    return this.status === 422;
  }
}

function joinUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${p}`;
}

type ApiRequestInit = Omit<RequestInit, "body"> & {
  json?: unknown;
  body?: BodyInit | null;
};

export async function apiJson<T>(path: string, init?: ApiRequestInit): Promise<T> {
  const { json, body: initBody, headers: hdrs, ...rest } = init ?? {};
  const headers = new Headers(hdrs);
  let body: BodyInit | undefined = initBody ?? undefined;
  if (json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(json);
  }
  const res = await fetch(joinUrl(path), {
    ...rest,
    headers,
    body,
  });
  const text = await res.text();
  const parsed = text ? (JSON.parse(text) as unknown) : null;
  if (!res.ok) {
    throw new ApiError(res.status, parsed);
  }
  return parsed as T;
}
