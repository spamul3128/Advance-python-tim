import { useEffect, useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import { ApiError, api } from "../lib/api";
import type { BotSummary } from "../lib/types";
import type { AppOutletContext } from "../components/AppShell";
import { BotPicker } from "../components/BotPicker";
import {
  ArchitectureDiagram,
  type Stage,
} from "../components/ArchitectureDiagram";
import { TechStack } from "../components/TechStack";
import { LogStream } from "../components/LogStream";
import { DataExplorer } from "../components/DataExplorer";
import { PredictionHistoryList } from "../components/PredictionHistoryList";

export default function HomePage() {
  const { stats, refreshStats } = useOutletContext<AppOutletContext>();
  const navigate = useNavigate();

  const [bots, setBots] = useState<BotSummary[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [botAId, setBotAId] = useState<number | null>(null);
  const [botBId, setBotBId] = useState<number | null>(null);
  const [predictError, setPredictError] = useState<string | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  const [activeStage, setActiveStage] = useState<Stage | null>(null);
  const [replayKey, setReplayKey] = useState(0);
  const [historyRefresh, setHistoryRefresh] = useState(0);

  useEffect(() => {
    let cancelled = false;
    api
      .listBots()
      .then((botList) => {
        if (!cancelled) setBots(botList);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const detail =
            err instanceof ApiError
              ? err.message
              : err instanceof Error
                ? err.message
                : "Unknown error";
          setLoadError(detail);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handlePredict = async () => {
    if (botAId === null || botBId === null || botAId === botBId) return;
    setIsPredicting(true);
    setPredictError(null);
    setReplayKey((k) => k + 1);

    try {
      setActiveStage("frontend");
      window.setTimeout(() => setActiveStage("sqlite"), 300);
      window.setTimeout(() => setActiveStage("llm"), 700);

      const result = await api.predict(botAId, botBId);
      setActiveStage("frontend");
      setHistoryRefresh((n) => n + 1);
      refreshStats();
      navigate(`/predictions/${result.prediction_id}`);
    } catch (err) {
      setPredictError(
        err instanceof Error ? err.message : "Prediction failed.",
      );
      setActiveStage(null);
    } finally {
      setIsPredicting(false);
      window.setTimeout(() => setActiveStage(null), 2500);
    }
  };

  return (
    <div className="space-y-10">
      {loadError && (
        <div className="panel border-loser/40">
          <div className="panel-header text-loser">Backend unreachable</div>
          <div className="panel-body text-sm whitespace-pre-wrap">
            {loadError}
          </div>
        </div>
      )}

      <BotPicker
        bots={bots}
        botAId={botAId}
        botBId={botBId}
        onChangeA={setBotAId}
        onChangeB={setBotBId}
        onPredict={handlePredict}
        isPredicting={isPredicting}
      />

      {predictError && (
        <div className="panel border-loser/40">
          <div className="panel-header text-loser">Prediction failed</div>
          <div className="panel-body text-sm">{predictError}</div>
        </div>
      )}

      <ArchitectureDiagram
        stats={stats}
        activeStage={activeStage}
        replayKey={replayKey}
      />

      <TechStack stats={stats} />

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <div className="xl:col-span-3">
          <LogStream />
        </div>
        <div className="xl:col-span-2">
          <div className="panel h-full flex flex-col">
            <div className="panel-header flex items-center justify-between">
              <span>Recent predictions</span>
              <Link
                to="/predictions"
                className="text-[11px] normal-case tracking-normal text-spark-400 hover:text-spark-300"
              >
                View all →
              </Link>
            </div>
            <div className="panel-body flex-1">
              <PredictionHistoryList
                limit={5}
                refreshSignal={historyRefresh}
                compact
              />
            </div>
          </div>
        </div>
      </div>

      <DataExplorer />
    </div>
  );
}
