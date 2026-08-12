// Mirrors backend/api/schemas.py — keep both files in sync.

export interface BotSummary {
  id: number;
  name: string;
  weight_class: string | null;
  weapon_type: string | null;
  team_name: string | null;
  country: string | null;
  image_url: string | null;
}

export interface MatchHistoryItem {
  id: number | null;
  opponent_id: number | null;
  opponent_name: string | null;
  won: boolean | null;
  method: string | null;
  season: string | null;
  round: string | null;
  episode: string | null;
  source_url?: string | null;
}

export interface SentimentPost {
  id?: string | null;
  title: string;
  body?: string | null;
  url?: string | null;
  score?: number | null;
  num_comments?: number | null;
  created_at?: string | null;
  subreddit?: string | null;
  sentiment?: string | null;
  text: string;
}

export interface SentimentItem {
  source: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  posts: SentimentPost[];
  sample_quotes: string[];
}

export interface BotDetail extends BotSummary {
  description: string | null;
  weapon_description: string | null;
  matches: MatchHistoryItem[];
  sentiment: SentimentItem[];
}

export interface BotReference {
  id: number;
  name: string;
}

// Audit trail attached to every prediction — describes the inputs that fed
// the LLM so the UI can show a "Sources" panel beside the report.
export interface BotSourceProfile {
  id: number;
  name: string;
  weight_class: string | null;
  weapon_type: string | null;
  weapon_description: string | null;
  team_name: string | null;
  country: string | null;
  image_url: string | null;
  source_url: string | null;
}

export interface BotSourceRecord {
  wins: number;
  losses: number;
  draws: number;
}

export interface BotSourceBundle {
  profile: BotSourceProfile;
  record: BotSourceRecord;
  matches: MatchHistoryItem[];
  sentiment: SentimentItem[];
}

export interface PredictionSources {
  bot_a: BotSourceBundle;
  bot_b: BotSourceBundle;
}

export interface EvidenceFact {
  id: string;
  category: string;
  bot: string;
  label: string;
  detail: string;
  source_url?: string | null;
  source_name?: string | null;
}

export interface FactCitation {
  fact_id: string;
  claim: string;
  supports: string;
}

export interface PredictionResponse {
  prediction_id: number;
  bot_a: BotReference;
  bot_b: BotReference;
  winner_id: number | null;
  winner: string;
  confidence: number;
  method_prediction: string;
  key_factors: string[];
  weapon_matchup: string;
  narrative: string;
  x_factor: string;
  reasoning_steps: string[];
  evidence_citations: string[];
  fact_citations: FactCitation[];
  evidence_catalog: EvidenceFact[];
  model: string;
  cached: boolean;
  sources: PredictionSources;
}

export interface PredictionListItem {
  id: number;
  bot_a: BotReference;
  bot_b: BotReference;
  winner_id: number | null;
  winner_name: string | null;
  confidence: number | null;
  created_at: string;
  model: string | null;
}

export interface StatsResponse {
  bots: number;
  matches: number;
  predictions: number;
  sentiment_rows: number;
  llm_provider: string;
  llm_model: string;
}

// Logs / live activity feed.
export interface LogEntry {
  id: number;
  timestamp: string;
  level: string;
  logger: string;
  message: string;
}

export interface LogStreamResponse {
  entries: LogEntry[];
  cursor: number;
}

// Data explorer — generic page envelope.
export interface ExplorerPage<T> {
  total: number;
  limit: number;
  offset: number;
  items: T[];
}

export interface ExplorerBotRow {
  id: number;
  name: string;
  weight_class: string | null;
  weapon_type: string | null;
  team_name: string | null;
  country: string | null;
  source_url: string | null;
  scraped_at: string | null;
}

export interface ExplorerMatchRow {
  id: number;
  bot_a_id: number | null;
  bot_a_name: string | null;
  bot_b_id: number | null;
  bot_b_name: string | null;
  winner_id: number | null;
  winner_name: string | null;
  method: string | null;
  season: string | null;
  episode: string | null;
  round: string | null;
  source_url: string | null;
  scraped_at: string | null;
}

export interface ExplorerSentimentRow {
  id: number;
  bot_id: number | null;
  bot_name: string | null;
  source: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  posts: SentimentPost[];
  sample_quotes: string[];
  scraped_at: string | null;
}

export interface ExplorerPredictionRow {
  id: number;
  bot_a_id: number | null;
  bot_a_name: string | null;
  bot_b_id: number | null;
  bot_b_name: string | null;
  winner_id: number | null;
  winner_name: string | null;
  confidence: number | null;
  model: string | null;
  created_at: string;
}

export type ExplorerTable = "bots" | "matches" | "sentiment" | "predictions";
