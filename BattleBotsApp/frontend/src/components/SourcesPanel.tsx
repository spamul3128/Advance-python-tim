/**
 * SourcesPanel — shows the exact data points that fed the LLM.
 *
 * Two columns (one per bot) each containing:
 *   - profile snapshot (weapon, team, country, source URL)
 *   - W/L/D record
 *   - match history table (recent first)
 *   - sentiment rows (Reddit/X)
 *
 * Collapsed by default to keep the report focused, but the toggle is
 * prominent so users discover it.
 */

import { useState } from "react";
import clsx from "clsx";
import type {
  BotSourceBundle,
  MatchHistoryItem,
  PredictionSources,
  SentimentItem,
  SentimentPost,
} from "../lib/types";
import { RedditPostCard } from "./RedditPostCard";

interface Props {
  sources: PredictionSources;
  winnerName: string;
}

export function SourcesPanel({ sources, winnerName }: Props) {
  const [open, setOpen] = useState(false);
  const totalMatches =
    sources.bot_a.matches.length + sources.bot_b.matches.length;
  const totalSentiment =
    sources.bot_a.sentiment.length + sources.bot_b.sentiment.length;

  return (
    <div className="panel">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="panel-header w-full flex items-center justify-between hover:bg-white/5 transition"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2">
          <span>Sources & Evidence</span>
          <span className="tag text-[10px]">
            {totalMatches} matches · {totalSentiment} sentiment rows
          </span>
        </span>
        <span className="text-xs font-mono text-slate-400">
          {open ? "Hide ▲" : "Show ▼"}
        </span>
      </button>
      {open && (
        <div className="panel-body grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BotSourceColumn
            bundle={sources.bot_a}
            isWinner={
              winnerName.toLowerCase() ===
              sources.bot_a.profile.name.toLowerCase()
            }
            sideLabel="Fighter A"
          />
          <BotSourceColumn
            bundle={sources.bot_b}
            isWinner={
              winnerName.toLowerCase() ===
              sources.bot_b.profile.name.toLowerCase()
            }
            sideLabel="Fighter B"
          />
        </div>
      )}
    </div>
  );
}

function BotSourceColumn({
  bundle,
  isWinner,
  sideLabel,
}: {
  bundle: BotSourceBundle;
  isWinner: boolean;
  sideLabel: string;
}) {
  const { profile, record, matches, sentiment } = bundle;
  return (
    <div className="space-y-4">
      <div
        className={clsx(
          "rounded-xl border px-4 py-3",
          isWinner
            ? "border-winner/40 bg-winner/5"
            : "border-white/10 bg-white/[0.02]",
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              {sideLabel}
            </div>
            <div className="text-lg font-semibold text-white mt-0.5">
              {profile.name}
            </div>
            <div className="text-xs text-slate-400 mt-1 space-x-2">
              {profile.weapon_type && <span>{profile.weapon_type}</span>}
              {profile.team_name && <span>· {profile.team_name}</span>}
              {profile.country && <span>· {profile.country}</span>}
            </div>
          </div>
          <RecordPill record={record} />
        </div>
        {profile.weapon_description && (
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            {profile.weapon_description}
          </p>
        )}
        {profile.source_url && (
          <a
            href={profile.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] font-mono text-spark-400 hover:text-spark-300 mt-2 inline-block underline-offset-2 hover:underline"
          >
            source ↗
          </a>
        )}
      </div>

      <MatchHistoryList matches={matches} />
      <SentimentList sentiment={sentiment} />
    </div>
  );
}

function RecordPill({
  record,
}: {
  record: { wins: number; losses: number; draws: number };
}) {
  return (
    <div className="text-right">
      <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
        Record
      </div>
      <div className="font-mono text-sm mt-0.5">
        <span className="text-winner">{record.wins}W</span>
        <span className="text-slate-500 mx-1">·</span>
        <span className="text-loser">{record.losses}L</span>
        {record.draws > 0 && (
          <>
            <span className="text-slate-500 mx-1">·</span>
            <span className="text-slate-300">{record.draws}D</span>
          </>
        )}
      </div>
    </div>
  );
}

function MatchHistoryList({ matches }: { matches: MatchHistoryItem[] }) {
  if (matches.length === 0) {
    return (
      <SectionShell title="Match history">
        <p className="text-xs text-slate-500 italic">
          No matches on file for this bot.
        </p>
      </SectionShell>
    );
  }
  // Cap at the most recent 15 — anything deeper isn't going to be the
  // model's decisive evidence anyway and the panel gets unwieldy.
  const display = matches.slice(0, 15);
  return (
    <SectionShell title={`Match history (${matches.length})`}>
      <ul className="space-y-1.5">
        {display.map((m, i) => (
          <li
            key={i}
            className="text-xs flex items-center gap-2 font-mono"
          >
            <OutcomeBadge won={m.won} />
            <span className="text-slate-200">
              vs {m.opponent_name ?? "Unknown"}
            </span>
            {m.method && (
              <span className="text-slate-400">· {m.method}</span>
            )}
            {m.season && (
              <span className="text-slate-500 ml-auto">{m.season}</span>
            )}
            {m.source_url && (
              <a
                href={m.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-spark-400 hover:text-spark-300 text-[10px] underline-offset-2 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                ↗
              </a>
            )}
          </li>
        ))}
      </ul>
      {matches.length > display.length && (
        <p className="text-[11px] text-slate-500 mt-2 font-mono">
          + {matches.length - display.length} more older matches
        </p>
      )}
    </SectionShell>
  );
}

function OutcomeBadge({ won }: { won: boolean | null }) {
  const label = won === true ? "W" : won === false ? "L" : "D";
  const tone =
    won === true
      ? "bg-winner/20 text-winner border-winner/40"
      : won === false
        ? "bg-loser/15 text-loser border-loser/40"
        : "bg-white/5 text-slate-300 border-white/10";
  return (
    <span
      className={clsx(
        "inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-bold border",
        tone,
      )}
      aria-label={`Outcome: ${label}`}
    >
      {label}
    </span>
  );
}

function SentimentList({ sentiment }: { sentiment: SentimentItem[] }) {
  if (sentiment.length === 0) {
    return (
      <SectionShell title="Fan sentiment">
        <p className="text-xs text-slate-500 italic">
          No sentiment data scraped yet.
        </p>
      </SectionShell>
    );
  }
  return (
    <SectionShell title="Fan sentiment">
      <div className="space-y-3">
        {sentiment.map((s, i) => (
          <div
            key={i}
            className="rounded-md bg-white/[0.03] border border-white/5 p-3"
          >
            <div className="flex items-center justify-between text-[11px] font-mono">
              <span className="uppercase tracking-wider text-slate-400">
                {s.source}
              </span>
              <span>
                <span className="text-winner">+{s.positive_count}</span>
                <span className="text-slate-500 mx-1">/</span>
                <span className="text-loser">-{s.negative_count}</span>
                <span className="text-slate-500 mx-1">/</span>
                <span className="text-slate-400">={s.neutral_count}</span>
              </span>
            </div>
            {displayPosts(s).length > 0 && (
              <ul className="mt-2 space-y-2">
                {displayPosts(s)
                  .slice(0, 4)
                  .map((post, q) => (
                    <li key={post.id ?? q}>
                      <RedditPostCard post={post} />
                    </li>
                  ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </SectionShell>
  );
}

/** Prefer structured posts; fall back to legacy quote strings. */
function displayPosts(s: SentimentItem): SentimentPost[] {
  if (s.posts?.length) {
    return s.posts;
  }
  return (s.sample_quotes ?? []).map((quote, i) => ({
    id: `legacy-${i}`,
    title: quote,
    body: null,
    url: null,
    score: null,
    num_comments: null,
    created_at: null,
    subreddit: null,
    sentiment: null,
    text: quote,
  }));
}

function SectionShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-slate-500 mb-2">
        {title}
      </div>
      {children}
    </div>
  );
}
