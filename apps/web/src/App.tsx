import { Link, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { DemoHelpPage } from "./presentation/pages/DemoHelpPage";
import { TalentDetailPage } from "./presentation/pages/TalentDetailPage";
import { TalentsPage } from "./presentation/pages/TalentsPage";
import { TemplatesPage } from "./presentation/pages/TemplatesPage";
import { paths } from "./presentation/routes/paths";

function menuItemClass({ isActive }: { isActive: boolean }): string {
  return [
    "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-slate-200 text-slate-900" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  ].join(" ");
}

export function App() {
  return (
    <div className="flex min-h-screen bg-white text-slate-900 antialiased">
      <aside className="flex w-52 shrink-0 flex-col border-r border-slate-200 bg-slate-50">
        <nav className="flex flex-1 flex-col gap-0.5 p-3" aria-label="メインメニュー">
          <NavLink to={paths.talents} className={menuItemClass}>
            人材
          </NavLink>
          <NavLink to={paths.templates} className={menuItemClass}>
            テンプレート
          </NavLink>
        </nav>
        <div className="border-t border-slate-200 px-3 py-2">
          <Link
            to={paths.demo}
            className="text-[10px] leading-tight text-slate-400 hover:text-slate-500"
            title="デモの流れ（補助）"
          >
            デモ手順
          </Link>
        </div>
      </aside>
      <main className="min-w-0 flex-1 overflow-auto p-6">
        <Routes>
          <Route path="/" element={<Navigate to={paths.talents} replace />} />
          <Route path={paths.talents} element={<TalentsPage />} />
          <Route path="/talents/:talentId" element={<TalentDetailPage />} />
          <Route path={paths.templates} element={<TemplatesPage />} />
          <Route path={paths.demo} element={<DemoHelpPage />} />
        </Routes>
      </main>
    </div>
  );
}
