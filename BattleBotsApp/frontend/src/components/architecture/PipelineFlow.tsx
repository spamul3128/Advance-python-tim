import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";
import {
  STEP_INFO,
  VISUAL_STEPS,
  type VisualStep,
} from "./types";

interface PipelineFlowProps {
  activeStep: VisualStep;
  compact?: boolean;
}

export function PipelineFlow({ activeStep, compact = false }: PipelineFlowProps) {
  const activeIndex = VISUAL_STEPS.indexOf(activeStep);
  const caption = STEP_INFO[activeStep].caption;
  const progress = activeIndex / (VISUAL_STEPS.length - 1);

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div
        className={clsx(
          compact
            ? "flex flex-col gap-5"
            : "grid grid-cols-4 gap-3 relative pt-2",
        )}
      >
        {!compact && (
          <div
            className="absolute top-[38px] left-[12.5%] right-[12.5%] h-px bg-white/10"
            aria-hidden
          />
        )}
        {!compact && (
          <motion.div
            className="absolute top-[38px] left-[12.5%] h-px bg-gradient-to-r from-signal-500 to-spark-400 origin-left"
            aria-hidden
            animate={{ width: `${progress * 75}%` }}
            transition={{ type: "spring", stiffness: 90, damping: 20 }}
          />
        )}

        {VISUAL_STEPS.map((step, i) => {
          const info = STEP_INFO[step];
          const isActive = step === activeStep;
          const isPast = i < activeIndex;

          return (
            <div
              key={step}
              className={clsx(
                "flex flex-col items-center text-center",
                compact && "flex-row gap-4 text-left items-center",
              )}
            >
              <motion.div
                className={clsx(
                  "relative flex h-16 w-16 shrink-0 items-center justify-center rounded-xl border text-2xl",
                  isActive &&
                    "border-signal-400/80 bg-signal-500/10 shadow-[0_0_20px_rgba(34,211,238,0.2)]",
                  !isActive && isPast && "border-white/15 bg-white/5",
                  !isActive && !isPast && "border-white/8 bg-ink-900/50 opacity-45",
                )}
                animate={{ scale: isActive ? 1.06 : 1 }}
                transition={{ type: "spring", stiffness: 280, damping: 22 }}
              >
                {info.icon}
              </motion.div>

              <div className={clsx("mt-2.5 min-w-0", compact && "mt-0")}>
                <div
                  className={clsx(
                    "text-sm font-semibold",
                    isActive ? "text-white" : "text-slate-400",
                  )}
                >
                  {info.title}
                </div>
                <div className="text-[11px] text-slate-500">{info.subtitle}</div>
              </div>
            </div>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.p
          key={activeStep}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="mt-7 text-sm text-slate-400 text-center leading-relaxed max-w-xl mx-auto"
        >
          {caption}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}
