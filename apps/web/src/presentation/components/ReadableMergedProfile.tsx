/** マージ済みプロフィールなど、任意の JSON 互換オブジェクトを画面向けに整形表示する */

const MAX_DEPTH = 24;

function labelizeKey(key: string): string {
  return key.replace(/_/g, " ");
}

function ProfileValue({ value, depth }: { value: unknown; depth: number }) {
  if (depth > MAX_DEPTH) {
    return <span className="text-xs text-amber-700">（ネストが深すぎるため省略）</span>;
  }

  if (value === null || value === undefined) {
    return <span className="text-slate-400">—</span>;
  }

  if (typeof value === "boolean") {
    return <span>{value ? "はい" : "いいえ"}</span>;
  }

  if (typeof value === "number" || typeof value === "bigint") {
    return <span className="tabular-nums">{String(value)}</span>;
  }

  if (typeof value === "string") {
    return (
      <p className="whitespace-pre-wrap break-words text-slate-800 [overflow-wrap:anywhere]">{value}</p>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-slate-400">（項目なし）</span>;
    }

    const allObjects =
      value.every((item) => item !== null && typeof item === "object" && !Array.isArray(item));

    if (allObjects) {
      return (
        <ol className="mt-1 list-decimal space-y-3 pl-5 text-slate-800">
          {value.map((item, i) => (
            <li key={i} className="marker:text-slate-400">
              <ProfileRecord record={item as Record<string, unknown>} depth={depth + 1} />
            </li>
          ))}
        </ol>
      );
    }

    return (
      <ul className="mt-1 list-disc space-y-1 pl-5 text-slate-800">
        {value.map((item, i) => (
          <li key={i}>
            <ProfileValue value={item} depth={depth + 1} />
          </li>
        ))}
      </ul>
    );
  }

  if (typeof value === "object") {
    return <ProfileRecord record={value as Record<string, unknown>} depth={depth + 1} />;
  }

  return <code className="rounded bg-slate-100 px-1 text-xs">{String(value)}</code>;
}

function ProfileRecord({ record, depth }: { record: Record<string, unknown>; depth: number }) {
  const entries = Object.entries(record).sort(([a], [b]) => a.localeCompare(b, "ja"));

  if (entries.length === 0) {
    return <span className="text-slate-400">（空のオブジェクト）</span>;
  }

  return (
    <dl className="space-y-3 border-l-2 border-slate-200 pl-3">
      {entries.map(([key, val]) => (
        <div key={key}>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labelizeKey(key)}</dt>
          <dd className="mt-0.5 text-sm">
            <ProfileValue value={val} depth={depth} />
          </dd>
        </div>
      ))}
    </dl>
  );
}

type Props = {
  data: Record<string, unknown>;
  className?: string;
};

export function ReadableMergedProfile({ data, className = "" }: Props) {
  return (
    <div className={`min-w-0 text-sm ${className}`}>
      <ProfileRecord record={data} depth={0} />
    </div>
  );
}
