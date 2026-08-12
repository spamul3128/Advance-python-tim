// Tiny fetch wrapper around the FastAPI backend.
//
// We don't pull in a heavy data-fetching library — the surface is small
// (3 GETs and 1 POST) and React Query would be overkill for this scope.

import type {
  BotDetail,
  BotSummary,
  ExplorerBotRow,
  ExplorerMatchRow,
  ExplorerPage,
  ExplorerPredictionRow,
  ExplorerSentimentRow,
  LogStreamResponse,
  PredictionListItem,
  PredictionResponse,
  StatsResponse,
} from "./types";

function isLocalDevBackend(url: string): boolean {
  try {
    const u = new URL(url);
    return (
      u.port === "8000" &&
      (u.hostname === "localhost" || u.hostname === "127.0.0.1")
    );
  } catch {
    return false;
  }
}

/** Backend origin. In dev, routes through Vite proxy `/api` when targeting local :8000. */
export function getApiBase(): string {
  const fromEnv = (import.meta.env.VITE_API_BASE as string | undefined)?.trim();
  if (import.meta.env.DEV) {
    if (!fromEnv || isLocalDevBackend(fromEnv)) return "/api";
  }
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  return "http://localhost:8000";
}

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  let response: Response;
  try {
    const base = getApiBase();
    response = await fetch(`${base}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      ...init,
    });
  } catch (err) {
    const hint =
      import.meta.env.DEV
        ? "Start the API: uv run uvicorn backend.main:app --reload --port 8000"
        : "Check that the backend is running and VITE_API_BASE is correct.";
    const msg =
      err instanceof Error && err.message === "Failed to fetch"
        ? `Network error — could not reach the API at ${getApiBase()}. ${hint}`
        : err instanceof Error
          ? err.message
          : "Network error";
    throw new ApiError(msg, 0);
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

// Build a query string with only defined params — keeps the URL clean and
// makes the request loggable in dev tools.
function qs(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const s = search.toString();
  return s ? `?${s}` : "";
}

export const api = {
  health: () => request<{ status: string; timestamp: string }>("/health"),
  stats: () => request<StatsResponse>("/stats"),
  listBots: () => request<BotSummary[]>("/bots"),
  getBot: (id: number) => request<BotDetail>(`/bots/${id}`),
  predict: (botAId: number, botBId: number, forceRefresh = false) =>
    request<PredictionResponse>("/predict", {
      method: "POST",
      body: JSON.stringify({
        bot_a_id: botAId,
        bot_b_id: botBId,
        force_refresh: forceRefresh,
      }),
    }),
  listPredictions: (limit = 20) =>
    request<PredictionListItem[]>(`/predictions?limit=${limit}`),
  getPrediction: (id: number) =>
    request<PredictionResponse>(`/predictions/${id}`),
  logs: (after = 0, limit = 200) =>
    request<LogStreamResponse>(`/logs${qs({ after, limit })}`),
  explorer: {
    bots: (limit = 50, offset = 0) =>
      request<ExplorerPage<ExplorerBotRow>>(
        `/explorer/bots${qs({ limit, offset })}`,
      ),
    matches: (limit = 50, offset = 0, botId?: number) =>
      request<ExplorerPage<ExplorerMatchRow>>(
        `/explorer/matches${qs({ limit, offset, bot_id: botId })}`,
      ),
    sentiment: (limit = 50, offset = 0) =>
      request<ExplorerPage<ExplorerSentimentRow>>(
        `/explorer/sentiment${qs({ limit, offset })}`,
      ),
    predictions: (limit = 50, offset = 0) =>
      request<ExplorerPage<ExplorerPredictionRow>>(
        `/explorer/predictions${qs({ limit, offset })}`,
      ),
  },
};

export { ApiError };
