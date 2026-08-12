/**
 * DataExplorer — read-only browser over the SQLite tables.
 *
 * Tabs:
 *   - Bots
 *   - Matches (with optional bot filter)
 *   - Sentiment
 *   - Predictions
 *
 * Each tab is paginated (25/page by default) and shares a single shell so
 * adding a fifth table later is one render function + one route.
 *
 * The four <Table*> components live next to the explorer in `DataExplorerTables.tsx`
 * to keep this file focused on layout + state.
 */

import { useCallback, useEffect, useState } from "react";
import clsx from "clsx";
import { api } from "../lib/api";
import type {
  ExplorerBotRow,
  ExplorerMatchRow,
  ExplorerPage,
  ExplorerPredictionRow,
  ExplorerSentimentRow,
  ExplorerTable,
} from "../lib/types";
import {
  TableBots,
  TableMatches,
  TablePredictions,
  TableSentiment,
} from "./DataExplorerTables";

const PAGE_SIZE = 25;

const TABS: { id: ExplorerTable; label: string }[] = [
  { id: "bots", label: "Bots" },
  { id: "matches", label: "Matches" },
  { id: "sentiment", label: "Sentiment" },
  { id: "predictions", label: "Predictions" },
];

type AnyPage =
  | ExplorerPage<ExplorerBotRow>
  | ExplorerPage<ExplorerMatchRow>
  | ExplorerPage<ExplorerSentimentRow>
  | ExplorerPage<ExplorerPredictionRow>;

export function DataExplorer() {
  const [tab, setTab] = useState<ExplorerTable>("bots");
  const [offset, setOffset] = useState(0);
  const [page, setPage] = useState<AnyPage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPage = useCallback(
    async (which: ExplorerTable, nextOffset: number) => {
      setLoading(true);
      setError(null);
      try {
        let next: AnyPage;
        switch (which) {
          case "bots":
            next = await api.explorer.bots(PAGE_SIZE, nextOffset);
            break;
          case "matches":
            next = await api.explorer.matches(PAGE_SIZE, nextOffset);
            break;
          case "sentiment":
            next = await api.explorer.sentiment(PAGE_SIZE, nextOffset);
            break;
          case "predictions":
            next = await api.explorer.predictions(PAGE_SIZE, nextOffset);
            break;
        }
        setPage(next);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data.");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  // Re-fetch whenever the tab or offset changes. We reset the offset when the
  // user switches tabs so the new view starts at page 1.
  useEffect(() => {
    fetchPage(tab, offset);
  }, [tab, offset, fetchPage]);

  const handleTabChange = (next: ExplorerTable) => {
    if (next === tab) return;
    setTab(next);
    setOffset(0);
    setPage(null);
  };

  const total = page?.total ?? 0;
  const currentEnd = page ? Math.min(offset + page.items.length, total) : 0;
  const canPrev = offset > 0;
  const canNext = total > offset + PAGE_SIZE;

  return (
    <div className="panel">
      <div className="panel-header flex items-center justify-between gap-3 flex-wrap">
        <span>Data Explorer</span>
        <div className="flex items-center bg-white/5 rounded-md border border-white/10 overflow-hidden">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => handleTabChange(t.id)}
              className={clsx(
                "px-3 py-1.5 text-[11px] font-mono uppercase tracking-wider transition",
                tab === t.id
                  ? "bg-spark-500/30 text-spark-200"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5",
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="panel-body">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-3">
          <span>
            {page ? (
              <>
                Showing{" "}
                <span className="text-slate-200">
                  {total === 0 ? 0 : offset + 1}–{currentEnd}
                </span>{" "}
                of <span className="text-slate-200">{total}</span> rows
              </>
            ) : loading ? (
              "Loading…"
            ) : (
              " "
            )}
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={!canPrev || loading}
              onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
              className="px-2.5 py-1 rounded-md border border-white/10 hover:bg-white/5 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              ← Prev
            </button>
            <button
              type="button"
              disabled={!canNext || loading}
              onClick={() => setOffset((o) => o + PAGE_SIZE)}
              className="px-2.5 py-1 rounded-md border border-white/10 hover:bg-white/5 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        </div>

        {error && (
          <div className="text-loser text-sm mb-3">⚠ {error}</div>
        )}

        <div className="overflow-x-auto -mx-2">
          <div className="min-w-[680px] px-2">
            {page && tab === "bots" && (
              <TableBots rows={(page as ExplorerPage<ExplorerBotRow>).items} />
            )}
            {page && tab === "matches" && (
              <TableMatches
                rows={(page as ExplorerPage<ExplorerMatchRow>).items}
              />
            )}
            {page && tab === "sentiment" && (
              <TableSentiment
                rows={(page as ExplorerPage<ExplorerSentimentRow>).items}
              />
            )}
            {page && tab === "predictions" && (
              <TablePredictions
                rows={(page as ExplorerPage<ExplorerPredictionRow>).items}
              />
            )}
            {loading && page === null && (
              <p className="text-sm text-slate-500 italic">Loading rows…</p>
            )}
            {page && page.items.length === 0 && !loading && (
              <p className="text-sm text-slate-500 italic">
                No rows on this page.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
