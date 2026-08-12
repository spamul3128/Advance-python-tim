/**
 * How-it-works pipeline — plain language, four steps, gentle animation.
 * Maps internal Stage ids from prediction replay onto visual steps.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import clsx from "clsx";
import type { StatsResponse } from "../lib/types";
import { PipelineFlow } from "./architecture/PipelineFlow";
import {
  VISUAL_STEPS,
  stageToVisual,
  type Stage,
  type VisualStep,
} from "./architecture/types";

export type { Stage };

interface Props {
  stats?: StatsResponse;
  activeStage?: Stage | null;
  replayKey?: number;
}

export function ArchitectureDiagram({
  stats,
  activeStage,
}: Props) {
  const [ambientStep, setAmbientStep] = useState<VisualStep>("gather");
  const [fullscreen, setFullscreen] = useState(false);
  const [compact, setCompact] = useState(() =>
    typeof window !== "undefined" ? window.innerWidth < 640 : false,
  );

  const replayActive = activeStage != null;
  const activeStep = activeStage
    ? stageToVisual(activeStage)
    : ambientStep;

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 639px)");
    const onChange = () => setCompact(mq.matches);
    onChange();
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  // Ambient: cycle through the four steps slowly when idle.
  useEffect(() => {
    if (replayActive) return;
    const id = window.setInterval(() => {
      setAmbientStep((prev) => {
        const idx = VISUAL_STEPS.indexOf(prev);
        return VISUAL_STEPS[(idx + 1) % VISUAL_STEPS.length];
      });
    }, 4000);
    return () => window.clearInterval(id);
  }, [replayActive]);

  const closeFullscreen = useCallback(() => setFullscreen(false), []);
  const openFullscreen = useCallback(() => setFullscreen(true), []);

  useEffect(() => {
    if (!fullscreen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeFullscreen();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
    };
  }, [fullscreen, closeFullscreen]);

  const summary = useMemo(() => {
    if (!stats) return null;
    return `${stats.bots} bots · ${stats.matches} fights on record · ${stats.predictions} predictions made`;
  }, [stats]);

  const shell = (
    <>
      <header className="panel-header flex flex-wrap items-center justify-between gap-3">
        <span>How it works</span>
        <button
          type="button"
          onClick={fullscreen ? closeFullscreen : openFullscreen}
          className="btn-ghost text-[11px] font-mono uppercase tracking-wider"
        >
          {fullscreen ? "✕ Exit" : "⛶ Fullscreen"}
        </button>
      </header>

      <div
        className={clsx(
          "px-4 sm:px-8 py-8 sm:py-10",
          fullscreen && "flex-1 flex flex-col justify-center",
        )}
      >
        <PipelineFlow activeStep={activeStep} compact={compact && !fullscreen} />
      </div>

      {summary && (
        <div className="px-5 py-3 border-t border-white/5 text-center text-xs text-slate-500">
          {summary}
        </div>
      )}
    </>
  );

  if (fullscreen) {
    return (
      <div
        className="fixed inset-0 z-[200] flex flex-col bg-ink-950/98 backdrop-blur-md"
        role="dialog"
        aria-modal="true"
        aria-label="How it works fullscreen"
      >
        <div className="panel flex flex-col flex-1 min-h-0 m-3 md:m-6 border-white/10 overflow-hidden">
          {shell}
        </div>
      </div>
    );
  }

  return <div className="panel overflow-hidden">{shell}</div>;
}
