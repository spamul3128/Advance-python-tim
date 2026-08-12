/**
 * ScoutingReport — renders a PredictionResponse from the backend.
 *
 * Layout:
 *   - Top: winner banner + confidence meter
 *   - Middle: key-factors list + weapon matchup callout
 *   - Narrative paragraph + x-factor
 *   - Rationale (LLM reasoning steps + cited evidence)
 *   - Sources (data that fed the model — collapsible)
 */

import { motion } from "framer-motion";
import clsx from "clsx";
import type { PredictionResponse } from "../lib/types";
import { confidenceTone, formatConfidence } from "../lib/confidence";
import { FactReportPanel } from "./FactReportPanel";
import { SourcesPanel } from "./SourcesPanel";

interface Props {
  prediction: PredictionResponse;
}

const methodLabels: Record<string, string> = {
  KO: "Knockout",
  TKO: "Technical Knockout",
  JD: "Judges' Decision",
  UNCLEAR: "Outcome TBD",
};

export function ScoutingReport({ prediction }: Props) {
  const {
    bot_a,
    bot_b,
    winner,
    confidence,
    method_prediction,
    key_factors,
    weapon_matchup,
    narrative,
    x_factor,
    reasoning_steps,
    evidence_citations,
    fact_citations,
    evidence_catalog,
    model,
    cached,
    sources,
  } = prediction;

  const confidenceLabel = formatConfidence(confidence);
  const winnerIsA = winner.toLowerCase() === bot_a.name.toLowerCase();

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Header — winner + confidence */}
      <div className="panel">
        <div className="panel-header flex items-center justify-between">
          <span>Scouting Report</span>
          <div className="flex items-center gap-2">
            {cached && <span className="tag">Cached</span>}
            <span className="tag font-mono">{model}</span>
          </div>
        </div>
        <div className="panel-body">
          <div className="flex items-end justify-between gap-6">
            <div>
              <div className="text-xs font-mono uppercase tracking-wider text-slate-500">
                Projected Winner
              </div>
              <div className="text-4xl font-display mt-1 tracking-wide text-white">
                {winner}
              </div>
              <div className="text-sm text-slate-400 mt-1">
                via {methodLabels[method_prediction] ?? method_prediction}
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs font-mono uppercase tracking-wider text-slate-500">
                Confidence
              </div>
              <div
                className={clsx(
                  "text-4xl font-display tracking-wide mt-1",
                  confidenceTone(confidence),
                )}
              >
                {confidenceLabel}
              </div>
            </div>
          </div>

          {/* Bot vs Bot bar */}
          <div className="mt-6 grid grid-cols-2 gap-1 items-stretch">
            <div
              className={clsx(
                "rounded-l-xl border-y border-l border-white/5 px-4 py-3 transition",
                winnerIsA
                  ? "bg-winner/10 border-winner/30"
                  : "bg-loser/5 border-white/10 opacity-70",
              )}
            >
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                Fighter A
              </div>
              <div className="text-lg font-semibold">{bot_a.name}</div>
            </div>
            <div
              className={clsx(
                "rounded-r-xl border-y border-r border-white/5 px-4 py-3 transition text-right",
                !winnerIsA
                  ? "bg-winner/10 border-winner/30"
                  : "bg-loser/5 border-white/10 opacity-70",
              )}
            >
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                Fighter B
              </div>
              <div className="text-lg font-semibold">{bot_b.name}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Key factors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="panel">
          <div className="panel-header">Key Factors</div>
          <div className="panel-body">
            <ul className="space-y-2">
              {key_factors.map((factor, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="text-spark-400 font-mono text-xs mt-0.5">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span className="text-slate-200">{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">Weapon Matchup</div>
          <div className="panel-body text-sm leading-relaxed text-slate-200">
            {weapon_matchup}
          </div>
        </div>
      </div>

      {/* Narrative */}
      <div className="panel">
        <div className="panel-header">Narrative Breakdown</div>
        <div className="panel-body text-base leading-relaxed text-slate-200 whitespace-pre-wrap">
          {narrative}
        </div>
      </div>

      {/* X-factor */}
      <div className="panel border border-spark-500/30 shadow-spark">
        <div className="panel-header text-spark-300">X-Factor</div>
        <div className="panel-body text-base text-slate-100 italic">
          "{x_factor}"
        </div>
      </div>

      {/* Rationale — LLM reasoning steps + cited evidence. Only rendered if
          the model actually returned anything (older cached predictions may
          predate the schema). */}
      {(fact_citations.length > 0 || evidence_catalog.length > 0) && (
        <FactReportPanel
          catalog={evidence_catalog}
          citations={fact_citations}
        />
      )}

      {(reasoning_steps.length > 0 || evidence_citations.length > 0) && (
        <RationalePanel
          reasoningSteps={reasoning_steps}
          evidenceCitations={evidence_citations}
        />
      )}

      {/* Sources — what data fed the LLM. */}
      <SourcesPanel sources={sources} winnerName={winner} />
    </motion.div>
  );
}

function RationalePanel({
  reasoningSteps,
  evidenceCitations,
}: {
  reasoningSteps: string[];
  evidenceCitations: string[];
}) {
  return (
    <div className="panel">
      <div className="panel-header flex items-center gap-2">
        <span>LLM Rationale</span>
        <span className="tag text-[10px]">Chain of thought</span>
      </div>
      <div className="panel-body space-y-5">
        {reasoningSteps.length > 0 && (
          <div>
            <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-slate-500 mb-2">
              Reasoning steps
            </div>
            <ol className="space-y-2.5">
              {reasoningSteps.map((step, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="shrink-0 w-6 h-6 rounded-full bg-spark-500/15 border border-spark-500/40 text-spark-300 font-mono text-[11px] flex items-center justify-center">
                    {i + 1}
                  </span>
                  <span className="text-slate-200 leading-relaxed">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {evidenceCitations.length > 0 && (
          <div>
            <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-slate-500 mb-2">
              Evidence the model cited
            </div>
            <div className="flex flex-wrap gap-2">
              {evidenceCitations.map((cite, i) => (
                <span
                  key={i}
                  className="text-xs font-mono px-2.5 py-1 rounded-md bg-white/5 border border-white/10 text-slate-200"
                >
                  {cite}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
