import type { RankComparison, UpskillAdvice } from "@/types/ranking";

interface AdvisoryInsightsPanelProps {
  componentizedMode: boolean;
  rankComparisons: RankComparison[];
  upskillAdvice: UpskillAdvice[];
}

function toDisplayJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

export function AdvisoryInsightsPanel({
  componentizedMode,
  rankComparisons,
  upskillAdvice,
}: AdvisoryInsightsPanelProps) {
  if (!componentizedMode) {
    return (
      <section className="panel advisory-panel">
        <div className="panel-head">
          <h2>Advisory Insights</h2>
          <p>Enable componentized mode on the backend to emit comparisons and upskill recommendations.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel advisory-panel">
      <div className="panel-head">
        <h2>Advisory Insights</h2>
        <p>Componentized analysis generated rank narratives and development paths.</p>
      </div>

      <div className="insights-summary">
        <div>
          <span>Rank Comparisons</span>
          <strong>{rankComparisons.length}</strong>
        </div>
        <div>
          <span>Upskill Recommendations</span>
          <strong>{upskillAdvice.length}</strong>
        </div>
      </div>

      <div className="insights-grid">
        <div className="insights-column">
          <h3>Top Rank Comparison</h3>
          {rankComparisons.length === 0 ? (
            <p className="insight-empty">No rank comparison output in this run.</p>
          ) : (
            <pre>{toDisplayJson(rankComparisons[0])}</pre>
          )}
        </div>

        <div className="insights-column">
          <h3>Top Upskill Recommendation</h3>
          {upskillAdvice.length === 0 ? (
            <p className="insight-empty">No upskill recommendations in this run.</p>
          ) : (
            <pre>{toDisplayJson(upskillAdvice[0])}</pre>
          )}
        </div>
      </div>
    </section>
  );
}
