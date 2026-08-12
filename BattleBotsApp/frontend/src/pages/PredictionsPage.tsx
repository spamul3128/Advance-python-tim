import { Link } from "react-router-dom";
import { PredictionHistoryList } from "../components/PredictionHistoryList";

export default function PredictionsPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="font-display text-2xl sm:text-3xl tracking-wide">
          Prediction history
        </h2>
        <p className="text-sm text-slate-400 mt-2 max-w-xl">
          Every scouting report the model has generated. Click a matchup to open
          the full fact-backed report, sources, and confidence breakdown.
        </p>
      </div>

      <div className="panel">
        <div className="panel-header flex items-center justify-between">
          <span>All predictions</span>
          <Link
            to="/"
            className="text-[11px] normal-case tracking-normal text-spark-400 hover:text-spark-300"
          >
            New prediction →
          </Link>
        </div>
        <div className="panel-body">
          <PredictionHistoryList limit={100} />
        </div>
      </div>
    </div>
  );
}
