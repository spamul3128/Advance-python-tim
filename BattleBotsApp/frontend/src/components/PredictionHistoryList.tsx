/**
 * Clickable prediction history rows — navigate to /predictions/:id.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import clsx from "clsx";
import { api } from "../lib/api";
import { formatConfidence } from "../lib/confidence";
import type { PredictionListItem } from "../lib/types";

interface Props {
  limit?: number;
  refreshSignal?: number;
  selectedId?: number | null;
  compact?: boolean;
}

export function PredictionHistoryList({
  limit = 50,
  refreshSignal = 0,
  selectedId,
  compact = false,
}: Props) {
  const [items, setItems] = useState<PredictionListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    api
      .listPredictions(limit)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load history.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [limit, refreshSignal]);

  return (
    <>
      {error && <p className="text-loser text-sm mb-3">{error}</p>}
      {!items && !error && (
        <p className="text-slate-500 text-sm">Loading predictions…</p>
      )}
      {items && items.length === 0 && (
        <p className="text-slate-500 text-sm">
          No predictions yet.{" "}
          <Link to="/" className="text-spark-400 hover:text-spark-300">
            Pick two bots
          </Link>{" "}
          on the Predict page to generate the first report.
        </p>
      )}
      {items && items.length > 0 && (
        <ul className={clsx("space-y-2", compact ? "" : "space-y-3")}>
          {items.map((p) => (
            <motion.li
              key={p.id}
              initial={{ opacity: 0, x: -4 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <Link
                to={`/predictions/${p.id}`}
                className={clsx(
                  "block w-full rounded-xl border px-4 transition text-left",
                  compact ? "py-3" : "py-4",
                  selectedId === p.id
                    ? "border-spark-500/40 bg-spark-500/10"
                    : "border-white/5 bg-ink-800/60 hover:bg-white/[0.04] hover:border-white/10",
                )}
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div
                      className={clsx(
                        "font-semibold truncate",
                        compact ? "text-sm" : "text-base",
                      )}
                    >
                      {p.bot_a.name}{" "}
                      <span className="text-slate-500 font-normal">vs</span>{" "}
                      {p.bot_b.name}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5 font-mono">
                      {formatTimestamp(p.created_at)}
                      {p.model && (
                        <span className="ml-2 text-slate-600">{p.model}</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="text-xs text-slate-400">winner</div>
                    <div className="text-sm font-semibold text-winner">
                      {p.winner_name ?? "?"}
                    </div>
                    <div className="text-[10px] font-mono text-slate-500">
                      {p.confidence !== null
                        ? formatConfidence(p.confidence)
                        : ""}
                    </div>
                  </div>
                </div>
              </Link>
            </motion.li>
          ))}
        </ul>
      )}
    </>
  );
}

function formatTimestamp(iso: string): string {
  try {
    const d = new Date(iso.endsWith("Z") ? iso : `${iso}Z`);
    return d.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}
