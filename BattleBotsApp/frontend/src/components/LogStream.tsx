/**
 * LogStream — polls /logs every few seconds and renders a tail of recent
 * backend activity. Auto-scrolls to the bottom when new entries arrive (but
 * not if the user has scrolled up to read history — common UX courtesy).
 *
 * Polling instead of SSE keeps the backend simple; for our volume (a few
 * dozen lines per prediction) a 2s tick is plenty responsive.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import clsx from "clsx";
import { api, ApiError } from "../lib/api";
import type { LogEntry } from "../lib/types";

const POLL_INTERVAL_MS = 2000;
const MAX_ENTRIES = 300;

type LevelFilter = "ALL" | "ERROR" | "WARNING" | "INFO";

export function LogStream() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [cursor, setCursor] = useState<number>(0);
  const [paused, setPaused] = useState(false);
  const [filter, setFilter] = useState<LevelFilter>("ALL");
  const [error, setError] = useState<string | null>(null);

  // Track scroll position so we only autoscroll when the user is "at bottom".
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const atBottomRef = useRef(true);

  const fetchLogs = useCallback(async () => {
    try {
      let result = await api.logs(cursor, 200);

      // After a backend reload the in-memory log buffer resets (ids start at 1)
      // while our cursor may still point past the new tail — recover from head.
      if (result.entries.length === 0 && cursor > 0) {
        const head = await api.logs(0, 200);
        const tailId = head.entries.length
          ? head.entries[head.entries.length - 1].id
          : 0;
        if (tailId > 0 && tailId < cursor) {
          setEntries(
            head.entries.length > MAX_ENTRIES
              ? head.entries.slice(-MAX_ENTRIES)
              : head.entries,
          );
          setCursor(head.cursor);
          setError(null);
          return;
        }
      }

      setError(null);
      setCursor(result.cursor);

      if (result.entries.length === 0) return;

      setEntries((current) => {
        const merged = [...current, ...result.entries];
        return merged.length > MAX_ENTRIES
          ? merged.slice(merged.length - MAX_ENTRIES)
          : merged;
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to fetch logs.";
      setError(message);
    }
  }, [cursor]);

  // Polling loop. We stop polling when paused — that's the user signaling
  // "I want to read what's on screen without it scrolling away under me".
  useEffect(() => {
    if (paused) return;
    fetchLogs();
    const id = window.setInterval(fetchLogs, POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [paused, fetchLogs]);

  // Autoscroll-to-bottom whenever new entries land — only if the user is
  // already pinned to the bottom.
  useEffect(() => {
    if (!atBottomRef.current) return;
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [entries]);

  const onScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    // 24px slack so the user doesn't have to be pixel-perfect.
    atBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 24;
  };

  const visible = useMemo(() => {
    if (filter === "ALL") return entries;
    return entries.filter((entry) => entry.level === filter);
  }, [entries, filter]);

  return (
    <div className="panel">
      <div className="panel-header flex items-center justify-between gap-3">
        <span className="flex items-center gap-2">
          <span>Live Activity</span>
          <span
            className={clsx(
              "inline-flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider",
              paused ? "text-slate-500" : "text-winner",
            )}
          >
            <span
              className={clsx(
                "w-1.5 h-1.5 rounded-full",
                paused ? "bg-slate-500" : "bg-winner animate-pulse",
              )}
            />
            {paused ? "Paused" : "Streaming"}
          </span>
        </span>
        <div className="flex items-center gap-2">
          <FilterControl value={filter} onChange={setFilter} />
          <button
            type="button"
            onClick={() => setPaused((p) => !p)}
            className="text-[11px] font-mono px-2.5 py-1 rounded-md border border-white/10 hover:bg-white/5 text-slate-300"
          >
            {paused ? "Resume" : "Pause"}
          </button>
        </div>
      </div>
      <div
        ref={scrollRef}
        onScroll={onScroll}
        className="bg-ink-950/60 border-t border-white/5 font-mono text-[12px] leading-relaxed max-h-72 overflow-y-auto px-4 py-3"
      >
        {error && (
          <div className="text-loser text-xs mb-2">⚠ {error}</div>
        )}
        {visible.length === 0 && !error && (
          <div className="text-slate-500 italic text-xs">
            Waiting for backend activity… trigger a prediction to see logs.
          </div>
        )}
        {visible.map((entry) => (
          <LogLine key={entry.id} entry={entry} />
        ))}
      </div>
    </div>
  );
}

function FilterControl({
  value,
  onChange,
}: {
  value: LevelFilter;
  onChange: (v: LevelFilter) => void;
}) {
  const options: LevelFilter[] = ["ALL", "INFO", "WARNING", "ERROR"];
  return (
    <div className="flex items-center bg-white/5 rounded-md border border-white/10 text-[11px] font-mono overflow-hidden">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => onChange(opt)}
          className={clsx(
            "px-2.5 py-1 transition",
            value === opt
              ? "bg-spark-500/30 text-spark-200"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/5",
          )}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

function LogLine({ entry }: { entry: LogEntry }) {
  const levelColor = {
    ERROR: "text-loser",
    WARNING: "text-spark-400",
    INFO: "text-slate-300",
    DEBUG: "text-slate-500",
  }[entry.level] ?? "text-slate-300";
  return (
    <div className="flex gap-2 whitespace-pre-wrap break-words">
      <span className="text-slate-600 shrink-0">{shortTime(entry.timestamp)}</span>
      <span className={clsx("shrink-0 w-12", levelColor)}>{entry.level}</span>
      <span className="text-slate-500 shrink-0 truncate max-w-[10rem]">
        {shortLogger(entry.logger)}
      </span>
      <span className="text-slate-200 flex-1">{entry.message}</span>
    </div>
  );
}

function shortTime(ts: string): string {
  // Backend timestamps look like "2026-05-20 14:09:12" — keep just HH:MM:SS.
  const parts = ts.split(" ");
  return parts.length > 1 ? parts[1] : ts;
}

function shortLogger(name: string): string {
  // Drop the leading package path so the line stays compact.
  const parts = name.split(".");
  return parts.length <= 2 ? name : parts.slice(-2).join(".");
}
