import clsx from "clsx";
import type { StatsResponse } from "../lib/types";

interface StackItem {
  name: string;
  detail?: string;
}

interface StackCategory {
  label: string;
  items: StackItem[];
}

function buildCategories(stats?: StatsResponse): StackCategory[] {
  const llmName =
    stats?.llm_provider === "anthropic" ? "Anthropic Claude" : "OpenAI";
  const llmDetail = stats?.llm_model ?? "GPT or Claude";

  return [
    {
      label: "Data collection",
      items: [
        { name: "Bright Data", detail: "Web Unlocker API" },
        { name: "battlebots.com", detail: "Official bot profiles" },
        { name: "BattleBots Wiki", detail: "Fandom fight history" },
        { name: "Reddit", detail: "Fan sentiment & quotes" },
        { name: "BeautifulSoup + lxml", detail: "HTML parsing" },
      ],
    },
    {
      label: "Backend",
      items: [
        { name: "Python 3.10+", detail: "Scrapers & API" },
        { name: "FastAPI", detail: "REST API" },
        { name: "Uvicorn", detail: "ASGI server" },
        { name: "SQLite", detail: "Local database" },
        { name: "Pydantic", detail: "Config & validation" },
        { name: "httpx", detail: "HTTP client" },
      ],
    },
    {
      label: "AI",
      items: [
        { name: llmName, detail: llmDetail },
        { name: "OpenAI Embeddings", detail: "RAG over Reddit chunks" },
        { name: "OpenAI SDK", detail: "Optional provider" },
        { name: "Anthropic SDK", detail: "Optional provider" },
      ],
    },
    {
      label: "Frontend",
      items: [
        { name: "React 19", detail: "UI" },
        { name: "TypeScript", detail: "Type safety" },
        { name: "Vite", detail: "Dev server & build" },
        { name: "Tailwind CSS", detail: "Styling" },
        { name: "Framer Motion", detail: "Animations" },
      ],
    },
    {
      label: "Tooling",
      items: [
        { name: "uv", detail: "Python deps & venv" },
        { name: "pytest", detail: "Backend tests" },
        { name: "ESLint", detail: "Frontend lint" },
      ],
    },
  ];
}

interface Props {
  stats?: StatsResponse;
}

export function TechStack({ stats }: Props) {
  const categories = buildCategories(stats);

  return (
    <div className="panel overflow-hidden">
      <header className="panel-header">Tech stack</header>

      <div className="panel-body grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {categories.map((cat) => (
          <div key={cat.label}>
            <h3 className="text-[10px] font-mono uppercase tracking-[0.2em] text-slate-500 mb-3">
              {cat.label}
            </h3>
            <ul className="space-y-2">
              {cat.items.map((item, i) => (
                <li key={item.name}>
                  <div
                    className={clsx(
                      "rounded-lg border border-white/5 bg-white/[0.02] px-3 py-2",
                      cat.label === "AI" &&
                        i === 0 &&
                        "border-spark-500/25 bg-spark-500/5",
                    )}
                  >
                    <div className="text-sm font-medium text-slate-200">
                      {item.name}
                    </div>
                    {item.detail && (
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        {item.detail}
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
