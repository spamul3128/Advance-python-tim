/**
 * BotPicker — two side-by-side bot selection cards plus a "Predict" trigger.
 *
 * Why a custom dropdown instead of a `<select>`: the design needs weapon-class
 * tags + team line under the bot name, which native `<select>` can't render.
 */

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";
import type { BotSummary } from "../lib/types";

interface Props {
  bots: BotSummary[];
  botAId: number | null;
  botBId: number | null;
  onChangeA: (id: number | null) => void;
  onChangeB: (id: number | null) => void;
  onPredict: () => void;
  isPredicting: boolean;
}

export function BotPicker({
  bots,
  botAId,
  botBId,
  onChangeA,
  onChangeB,
  onPredict,
  isPredicting,
}: Props) {
  const canPredict =
    botAId !== null && botBId !== null && botAId !== botBId && !isPredicting;

  return (
    <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-stretch">
      <BotSlot
        side="A"
        bots={bots}
        excludeId={botBId}
        selectedId={botAId}
        onChange={onChangeA}
      />

      <div className="flex items-center justify-center md:py-6">
        <motion.button
          type="button"
          onClick={onPredict}
          disabled={!canPredict}
          className="btn-primary px-6 py-4 text-base relative"
          whileHover={canPredict ? { scale: 1.03 } : undefined}
          whileTap={canPredict ? { scale: 0.97 } : undefined}
        >
          {isPredicting ? (
            <span className="flex items-center gap-2">
              <Spinner /> Analyzing…
            </span>
          ) : (
            <>
              <span>Predict</span>
              <span className="text-xs opacity-70">→</span>
            </>
          )}
        </motion.button>
      </div>

      <BotSlot
        side="B"
        bots={bots}
        excludeId={botAId}
        selectedId={botBId}
        onChange={onChangeB}
      />
    </div>
  );
}

interface SlotProps {
  side: "A" | "B";
  bots: BotSummary[];
  selectedId: number | null;
  excludeId: number | null;
  onChange: (id: number | null) => void;
}

function BotSlot({ side, bots, selectedId, excludeId, onChange }: SlotProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const selected = bots.find((b) => b.id === selectedId) ?? null;

  const options = useMemo(() => {
    const q = query.trim().toLowerCase();
    return bots
      .filter((b) => b.id !== excludeId)
      .filter((b) =>
        q
          ? b.name.toLowerCase().includes(q) ||
            (b.weapon_type ?? "").toLowerCase().includes(q) ||
            (b.team_name ?? "").toLowerCase().includes(q)
          : true,
      );
  }, [bots, excludeId, query]);

  // When the dropdown is open we raise the whole slot above sibling panels —
  // otherwise the architecture diagram (which has its own backdrop-blur
  // stacking context) renders on top and clips the bot list.
  return (
    <div className={clsx("panel relative", open ? "z-40" : "z-10")}>
      <div className="panel-header flex items-center justify-between">
        <span>Fighter {side}</span>
        {selected && (
          <button
            type="button"
            onClick={() => onChange(null)}
            className="text-[10px] text-slate-500 hover:text-slate-200"
          >
            clear
          </button>
        )}
      </div>

      <div className="panel-body min-h-[7.5rem]">
        {selected ? (
          <SelectedBotPreview bot={selected} onChangeClick={() => setOpen((v) => !v)} />
        ) : (
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="w-full text-left rounded-xl border border-dashed border-white/10 px-4 py-6
              text-slate-400 hover:text-white hover:border-spark-500/60 transition"
          >
            <span className="text-sm font-mono uppercase tracking-wider">
              + Choose a bot
            </span>
          </button>
        )}
      </div>

      {open && (
        <div className="absolute z-50 left-0 right-0 top-full mt-2 panel max-h-72 overflow-hidden shadow-2xl">
          <div className="p-2 border-b border-white/5">
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search bots, weapons, teams…"
              className="w-full bg-ink-800 rounded-lg px-3 py-2 text-sm
                placeholder:text-slate-500 outline-none ring-0 focus:bg-ink-700"
            />
          </div>
          <div className="overflow-y-auto max-h-56">
            {options.length === 0 && (
              <div className="px-4 py-3 text-sm text-slate-500">No bots match.</div>
            )}
            {options.map((b) => (
              <button
                key={b.id}
                type="button"
                onClick={() => {
                  onChange(b.id);
                  setOpen(false);
                  setQuery("");
                }}
                className="w-full text-left px-4 py-2.5 hover:bg-white/5 transition"
              >
                <div className="text-sm font-semibold">{b.name}</div>
                <div className="text-xs text-slate-400">
                  {b.weapon_type ?? "Unknown weapon"} ·{" "}
                  {b.team_name ?? "Unknown team"}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SelectedBotPreview({
  bot,
  onChangeClick,
}: {
  bot: BotSummary;
  onChangeClick: () => void;
}) {
  return (
    <div className="flex items-start gap-4">
      <div
        className={clsx(
          "w-16 h-16 rounded-xl bg-ink-800 border border-white/5",
          "flex items-center justify-center text-2xl font-display",
          "text-spark-400 shrink-0",
        )}
      >
        {bot.name.slice(0, 2).toUpperCase()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xl font-display tracking-wide">{bot.name}</div>
        <div className="text-xs text-slate-400 mt-0.5 truncate">
          {bot.weapon_type ?? "Weapon unknown"}
        </div>
        <div className="text-xs text-slate-500 mt-0.5 truncate">
          {bot.team_name ?? "Team unknown"}
        </div>
        <button
          type="button"
          onClick={onChangeClick}
          className="mt-3 text-[10px] uppercase tracking-wider text-signal-400 hover:text-signal-500"
        >
          Change ↺
        </button>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeOpacity="0.25"
        strokeWidth="3"
      />
      <path
        d="M12 2a10 10 0 0 1 10 10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}
