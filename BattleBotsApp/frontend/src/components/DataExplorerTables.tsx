/**
 * Table renderers for each explorer tab. Kept in a separate file from
 * `DataExplorer.tsx` so the data-fetching shell stays focused.
 *
 * Each table component is pure presentation — it takes rows and renders. No
 * pagination, no state. That keeps them trivial to test in isolation and
 * makes the explorer easy to extend.
 */

import clsx from "clsx";
import { formatConfidence } from "../lib/confidence";
import type {
  ExplorerBotRow,
  ExplorerMatchRow,
  ExplorerPredictionRow,
  ExplorerSentimentRow,
} from "../lib/types";
import { RedditPostCard } from "./RedditPostCard";

// Shared cell + header styles. Defined once so every table looks uniform.
const TH =
  "text-left text-[10px] font-mono uppercase tracking-wider text-slate-500 px-3 py-2 border-b border-white/10";
const TD =
  "px-3 py-2 text-sm text-slate-200 border-b border-white/5 align-top";

export function TableBots({ rows }: { rows: ExplorerBotRow[] }) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className={TH}>Name</th>
          <th className={TH}>Weapon</th>
          <th className={TH}>Weight</th>
          <th className={TH}>Team</th>
          <th className={TH}>Country</th>
          <th className={TH}>Source</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id} className="hover:bg-white/[0.03]">
            <td className={clsx(TD, "font-semibold text-white")}>{r.name}</td>
            <td className={TD}>{r.weapon_type ?? "—"}</td>
            <td className={TD}>{r.weight_class ?? "—"}</td>
            <td className={TD}>{r.team_name ?? "—"}</td>
            <td className={TD}>{r.country ?? "—"}</td>
            <td className={TD}>
              {r.source_url ? (
                <a
                  href={r.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-spark-400 hover:text-spark-300 font-mono text-xs underline-offset-2 hover:underline"
                >
                  link ↗
                </a>
              ) : (
                <span className="text-slate-500">—</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function TableMatches({ rows }: { rows: ExplorerMatchRow[] }) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className={TH}>Bot A</th>
          <th className={TH}>Bot B</th>
          <th className={TH}>Winner</th>
          <th className={TH}>Method</th>
          <th className={TH}>Season</th>
          <th className={TH}>Round</th>
          <th className={TH}>Scraped</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id} className="hover:bg-white/[0.03]">
            <td className={TD}>{r.bot_a_name ?? `#${r.bot_a_id ?? "?"}`}</td>
            <td className={TD}>{r.bot_b_name ?? `#${r.bot_b_id ?? "?"}`}</td>
            <td className={clsx(TD, r.winner_name && "text-winner font-medium")}>
              {r.winner_name ?? <span className="text-slate-500">draw/?</span>}
            </td>
            <td className={TD}>
              <span className="font-mono text-xs">{r.method ?? "—"}</span>
            </td>
            <td className={TD}>{r.season ?? "—"}</td>
            <td className={TD}>{r.round ?? "—"}</td>
            <td className={clsx(TD, "text-slate-500 font-mono text-xs")}>
              {compactDate(r.scraped_at)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function TableSentiment({ rows }: { rows: ExplorerSentimentRow[] }) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className={TH}>Bot</th>
          <th className={TH}>Source</th>
          <th className={TH}>+</th>
          <th className={TH}>−</th>
          <th className={TH}>=</th>
          <th className={TH}>Sample post</th>
          <th className={TH}>Scraped</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id} className="hover:bg-white/[0.03]">
            <td className={clsx(TD, "font-medium")}>{r.bot_name ?? `#${r.bot_id}`}</td>
            <td className={TD}>
              <span className="font-mono text-xs uppercase">{r.source}</span>
            </td>
            <td className={clsx(TD, "text-winner font-mono")}>{r.positive_count}</td>
            <td className={clsx(TD, "text-loser font-mono")}>{r.negative_count}</td>
            <td className={clsx(TD, "text-slate-400 font-mono")}>{r.neutral_count}</td>
            <td className={clsx(TD, "max-w-md")}>
              {r.posts[0] ? (
                <RedditPostCard post={r.posts[0]} compact />
              ) : r.sample_quotes[0] ? (
                <span className="italic text-slate-300">
                  "{truncate(r.sample_quotes[0], 90)}"
                </span>
              ) : (
                "—"
              )}
            </td>
            <td className={clsx(TD, "text-slate-500 font-mono text-xs")}>
              {compactDate(r.scraped_at)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function TablePredictions({
  rows,
}: {
  rows: ExplorerPredictionRow[];
}) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className={TH}>Bot A</th>
          <th className={TH}>Bot B</th>
          <th className={TH}>Winner</th>
          <th className={TH}>Confidence</th>
          <th className={TH}>Model</th>
          <th className={TH}>Created</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id} className="hover:bg-white/[0.03]">
            <td className={TD}>{r.bot_a_name ?? `#${r.bot_a_id ?? "?"}`}</td>
            <td className={TD}>{r.bot_b_name ?? `#${r.bot_b_id ?? "?"}`}</td>
            <td className={clsx(TD, "text-winner font-medium")}>
              {r.winner_name ?? <span className="text-slate-500">—</span>}
            </td>
            <td className={clsx(TD, "font-mono")}>
              {r.confidence != null ? formatConfidence(r.confidence) : "—"}
            </td>
            <td className={clsx(TD, "font-mono text-xs")}>{r.model ?? "—"}</td>
            <td className={clsx(TD, "text-slate-500 font-mono text-xs")}>
              {compactDate(r.created_at)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function truncate(value: string, max: number): string {
  return value.length <= max ? value : value.slice(0, max - 1).trimEnd() + "…";
}

function compactDate(raw: string | null): string {
  if (!raw) return "—";
  // Most timestamps from the backend look like "2026-05-20 14:09:12" — strip
  // the year to save horizontal space.
  const trimmed = raw.replace(/\.\d+/, "").replace("T", " ");
  return trimmed.length > 5 ? trimmed.slice(5) : trimmed;
}
