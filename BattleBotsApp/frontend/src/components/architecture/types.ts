/** Internal stage ids — kept for prediction replay from App.tsx */
export type Stage =
  | "sources"
  | "brightdata"
  | "scrapers"
  | "sqlite"
  | "llm"
  | "frontend";

export const STAGES: Stage[] = [
  "sources",
  "brightdata",
  "scrapers",
  "sqlite",
  "llm",
  "frontend",
];

/** Four plain-language steps shown in the UI */
export type VisualStep = "gather" | "store" | "analyze" | "view";

export const VISUAL_STEPS: VisualStep[] = [
  "gather",
  "store",
  "analyze",
  "view",
];

export interface StepInfo {
  id: VisualStep;
  icon: string;
  title: string;
  subtitle: string;
  caption: string;
}

export const STEP_INFO: Record<VisualStep, StepInfo> = {
  gather: {
    id: "gather",
    icon: "🌐",
    title: "Gather",
    subtitle: "From the web",
    caption:
      "Bright Data visits BattleBots websites and fan forums to collect bot profiles, fight history, and what people are saying.",
  },
  store: {
    id: "store",
    icon: "🗄️",
    title: "Store",
    subtitle: "In a database",
    caption:
      "Everything is saved and organized — every bot, every match, every fan quote — ready to look up instantly.",
  },
  analyze: {
    id: "analyze",
    icon: "🧠",
    title: "Analyze",
    subtitle: "With AI",
    caption:
      "When you pick two bots, the AI reads their stats and writes a scouting report with a predicted winner.",
  },
  view: {
    id: "view",
    icon: "⚔️",
    title: "Predict",
    subtitle: "Your matchup",
    caption:
      "You choose any two bots and read the full scouting report — strengths, weaknesses, and who the AI thinks wins.",
  },
};

export function stageToVisual(stage: Stage): VisualStep {
  switch (stage) {
    case "sources":
    case "brightdata":
    case "scrapers":
      return "gather";
    case "sqlite":
      return "store";
    case "llm":
      return "analyze";
    case "frontend":
      return "view";
  }
}
