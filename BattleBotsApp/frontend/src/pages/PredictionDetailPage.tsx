import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import type { PredictionResponse } from "../lib/types";
import { ScoutingReport } from "../components/ScoutingReport";

export default function PredictionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const predictionId = Number(id);

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!Number.isFinite(predictionId) || predictionId <= 0) {
      setError("Invalid prediction id.");
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);
    setPrediction(null);

    api
      .getPrediction(predictionId)
      .then((result) => {
        if (!cancelled) setPrediction(result);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load prediction.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [predictionId]);

  return (
    <div className="space-y-6">
      <nav className="flex flex-wrap items-center gap-3 text-sm font-mono">
        <Link
          to="/predictions"
          className="text-slate-400 hover:text-spark-300 transition"
        >
          ← History
        </Link>
        <span className="text-slate-600">/</span>
        <Link to="/" className="text-slate-400 hover:text-spark-300 transition">
          Predict
        </Link>
      </nav>

      {loading && (
        <p className="text-sm text-slate-400 font-mono text-center py-12">
          Loading scouting report…
        </p>
      )}

      {error && !loading && (
        <div className="panel border-loser/40 max-w-xl">
          <div className="panel-header text-loser">Could not load report</div>
          <div className="panel-body text-sm space-y-3">
            <p>{error}</p>
            <Link to="/predictions" className="text-spark-400 hover:text-spark-300">
              Back to history
            </Link>
          </div>
        </div>
      )}

      {prediction && !loading && (
        <ScoutingReport prediction={prediction} />
      )}
    </div>
  );
}
