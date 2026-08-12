import clsx from "clsx";
import type { EvidenceFact, FactCitation } from "../lib/types";

interface Props {
  catalog: EvidenceFact[];
  citations: FactCitation[];
}

const supportTone: Record<string, string> = {
  winner: "border-winner/30 bg-winner/10 text-winner",
  loser: "border-loser/30 bg-loser/10 text-loser",
  neutral: "border-white/10 bg-white/5 text-slate-300",
};

export function FactReportPanel({ catalog, citations }: Props) {
  const citedIds = new Set(
    citations.map((c) => c.fact_id).filter(Boolean),
  );
  const citedFacts = catalog.filter((f) => citedIds.has(f.id));
  const uncited = catalog.filter((f) => !citedIds.has(f.id));

  if (catalog.length === 0) {
    return null;
  }

  return (
    <div className="panel border border-spark-500/20">
      <div className="panel-header flex items-center gap-2">
        <span>Fact Report</span>
        <span className="tag text-[10px]">
          {citedFacts.length} cited · {catalog.length} total
        </span>
      </div>
      <div className="panel-body space-y-6">
        {citations.length > 0 && (
          <section>
            <SectionTitle>Why this prediction</SectionTitle>
            <ul className="space-y-3">
              {citations.map((cite, i) => {
                const fact = catalog.find((f) => f.id === cite.fact_id);
                return (
                  <li
                    key={`${cite.fact_id}-${i}`}
                    className="rounded-lg border border-white/5 bg-white/[0.02] p-3"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        {cite.fact_id && (
                          <span className="text-[10px] font-mono text-spark-400">
                            [{cite.fact_id}]
                          </span>
                        )}
                        <p className="text-sm text-slate-200 mt-1 leading-relaxed">
                          {cite.claim}
                        </p>
                        {fact && (
                          <p className="text-[11px] text-slate-500 mt-1.5">
                            Source: {fact.label} — {fact.detail}
                          </p>
                        )}
                      </div>
                      <span
                        className={clsx(
                          "shrink-0 text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded border",
                          supportTone[cite.supports] ?? supportTone.neutral,
                        )}
                      >
                        {cite.supports}
                      </span>
                    </div>
                    {fact?.source_url && (
                      <a
                        href={fact.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block mt-2 text-[11px] font-mono text-spark-400 hover:text-spark-300 underline-offset-2 hover:underline"
                      >
                        View source ({fact.source_name ?? "link"}) ↗
                      </a>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        <section>
          <SectionTitle>All evidence on file</SectionTitle>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="text-[10px] font-mono uppercase tracking-wider text-slate-500 border-b border-white/10">
                  <th className="py-2 pr-3">ID</th>
                  <th className="py-2 pr-3">Fact</th>
                  <th className="py-2 pr-3">Detail</th>
                  <th className="py-2">Source</th>
                </tr>
              </thead>
              <tbody>
                {catalog.map((fact) => {
                  const used = citedIds.has(fact.id);
                  return (
                    <tr
                      key={fact.id}
                      className={clsx(
                        "border-b border-white/5 text-xs align-top",
                        used ? "bg-spark-500/5" : "opacity-80",
                      )}
                    >
                      <td className="py-2 pr-3 font-mono text-spark-400 whitespace-nowrap">
                        {fact.id}
                      </td>
                      <td className="py-2 pr-3 text-slate-200 max-w-[10rem]">
                        <div>{fact.label}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5 uppercase">
                          {fact.category} · Bot {fact.bot}
                        </div>
                      </td>
                      <td className="py-2 pr-3 text-slate-400 max-w-md">
                        {fact.detail}
                      </td>
                      <td className="py-2">
                        {fact.source_url ? (
                          <a
                            href={fact.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-mono text-spark-400 hover:text-spark-300 underline-offset-2 hover:underline"
                          >
                            {fact.source_name ?? "Open"} ↗
                          </a>
                        ) : (
                          <span className="text-slate-500">
                            {fact.source_name ?? "—"}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {uncited.length > 0 && citations.length > 0 && (
            <p className="text-[11px] text-slate-500 mt-3 font-mono">
              {uncited.length} facts were available but not cited in the rationale.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-slate-500 mb-2">
      {children}
    </div>
  );
}
