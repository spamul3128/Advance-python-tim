import clsx from "clsx";
import type { SentimentPost } from "../lib/types";

interface Props {
  post: SentimentPost;
  compact?: boolean;
}

export function RedditPostCard({ post, compact = false }: Props) {
  const meta = [
    post.created_at,
    post.score != null ? `${post.score}↑` : null,
    post.num_comments != null ? `${post.num_comments} comments` : null,
    post.subreddit ? `r/${post.subreddit}` : null,
  ]
    .filter(Boolean)
    .join(" · ");

  const title = post.title || post.text;
  const body = post.body?.trim();

  return (
    <article
      className={clsx(
        "rounded-md border border-white/5 bg-white/[0.02]",
        compact ? "p-2.5" : "p-3",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          {post.url ? (
            <a
              href={post.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[13px] font-medium text-spark-300 hover:text-spark-200 underline-offset-2 hover:underline leading-snug"
            >
              {title}
            </a>
          ) : (
            <div className="text-[13px] font-medium text-slate-200 leading-snug">
              {title}
            </div>
          )}
          {meta && (
            <div className="text-[10px] font-mono text-slate-500 mt-1">
              {meta}
            </div>
          )}
        </div>
        {post.sentiment && (
          <SentimentBadge label={post.sentiment} />
        )}
      </div>
      {body && !compact && (
        <p className="text-[12px] text-slate-400 mt-2 leading-relaxed line-clamp-4">
          {body}
        </p>
      )}
      {body && compact && (
        <p className="text-[11px] text-slate-500 mt-1.5 leading-snug line-clamp-2 italic">
          {body}
        </p>
      )}
    </article>
  );
}

function SentimentBadge({ label }: { label: string }) {
  const tone =
    label === "positive"
      ? "bg-winner/15 text-winner border-winner/30"
      : label === "negative"
        ? "bg-loser/15 text-loser border-loser/30"
        : "bg-white/5 text-slate-400 border-white/10";
  return (
    <span
      className={clsx(
        "shrink-0 text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded border",
        tone,
      )}
    >
      {label}
    </span>
  );
}
