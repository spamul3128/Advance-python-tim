import { useEffect, useMemo, useState, type ReactNode } from "react";
import { NavLink, Outlet } from "react-router-dom";
import clsx from "clsx";
import { api } from "../lib/api";
import type { StatsResponse } from "../lib/types";

export function AppShell() {
  const [stats, setStats] = useState<StatsResponse | undefined>();

  useEffect(() => {
    let cancelled = false;
    const load = () =>
      api.stats().then((s) => !cancelled && setStats(s)).catch(() => {});
    load();
    const id = window.setInterval(load, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const subtitle = useMemo(() => {
    if (!stats) return "Loading roster…";
    return `${stats.bots} bots · ${stats.matches} historical fights · ${stats.predictions} predictions · ${stats.llm_provider}`;
  }, [stats]);

  return (
    <div className="min-h-full flex flex-col">
      <header className="border-b border-white/5 bg-ink-900/60 backdrop-blur sticky top-0 z-30">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-10 py-5">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
            <div>
              <div className="text-[11px] font-mono uppercase tracking-[0.25em] text-spark-400">
                Bright Data × OpenAI
              </div>
              <h1 className="font-display text-3xl sm:text-4xl tracking-wide mt-0.5">
                <NavLink to="/" className="hover:text-spark-200 transition">
                  BattleBots AI Fight Predictor
                </NavLink>
              </h1>
            </div>
            {subtitle && (
              <div className="hidden md:block text-xs font-mono text-slate-400 text-right max-w-md">
                {subtitle}
              </div>
            )}
          </div>
          <nav className="mt-4 flex items-center gap-1 font-mono text-xs uppercase tracking-wider">
            <NavTab to="/" end>
              Predict
            </NavTab>
            <NavTab to="/predictions">History</NavTab>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-screen-2xl w-full mx-auto px-4 sm:px-6 lg:px-10 py-8 sm:py-10">
        <Outlet context={{ stats, refreshStats: () => api.stats().then(setStats).catch(() => {}) }} />
      </main>

      <footer className="border-t border-white/5 py-6 text-center text-xs text-slate-500 font-mono">
        Scraped via Bright Data Web Unlocker · Stored in SQLite · Predictions via LLM
      </footer>
    </div>
  );
}

function NavTab({
  to,
  end,
  children,
}: {
  to: string;
  end?: boolean;
  children: ReactNode;
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        clsx(
          "px-4 py-2 rounded-lg border transition",
          isActive
            ? "border-spark-500/40 bg-spark-500/15 text-spark-200"
            : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5",
        )
      }
    >
      {children}
    </NavLink>
  );
}

export type AppOutletContext = {
  stats?: StatsResponse;
  refreshStats: () => void;
};
