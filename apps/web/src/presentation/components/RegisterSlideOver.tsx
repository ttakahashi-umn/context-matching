import { useEffect, useId, type ReactNode } from "react";

type RegisterSlideOverProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  /** パネル幅（Tailwind）。例: max-w-md / max-w-2xl */
  panelMaxWidthClass?: string;
  children: ReactNode;
};

/**
 * 一覧画面から「登録」を開いたとき、右からスライドインする登録用パネル。
 */
export function RegisterSlideOver({
  open,
  onClose,
  title,
  panelMaxWidthClass = "max-w-md",
  children,
}: RegisterSlideOverProps) {
  const titleId = useId();

  useEffect(() => {
    if (!open) return;
    function onKey(ev: KeyboardEvent) {
      if (ev.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <div
      className={["fixed inset-0 z-40 flex justify-end", open ? "pointer-events-auto" : "pointer-events-none"].join(
        " ",
      )}
    >
      <button
        type="button"
        className={[
          "absolute inset-0 bg-slate-900/40 transition-opacity duration-300 ease-out",
          open ? "opacity-100" : "opacity-0",
        ].join(" ")}
        onClick={onClose}
        aria-label="オーバーレイを閉じる"
        tabIndex={open ? 0 : -1}
      />
      <aside
        className={[
          "relative flex h-full w-full flex-col border-l border-slate-200 bg-white shadow-xl transition-transform duration-300 ease-out",
          panelMaxWidthClass,
          open ? "translate-x-0" : "translate-x-full",
        ].join(" ")}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
      >
        <header className="flex shrink-0 items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
          <h2 id={titleId} className="text-base font-semibold text-slate-900">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-sm text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          >
            閉じる
          </button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto p-4">{children}</div>
      </aside>
    </div>
  );
}
