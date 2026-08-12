import type { RankComparison, UpskillAdvice } from "@/types/ranking";

interface AdvisoryInsightsPanelProps {
  componentizedMode: boolean;
  rankComparisons: RankComparison[];
  upskillAdvice: UpskillAdvice[];
}

function toLabel(text: string | undefined, fallback: string): string {
  if (!text || text.trim().length === 0) {
    return fallback;
  }
  return text.replace(/_/g, " ");
}

function toWeeksLabel(low?: number, high?: number): string {
  if (typeof low === "number" && typeof high === "number") {
    return low === high ? `${low} week${low === 1 ? "" : "s"}` : `${low}-${high} weeks`;
  }
  if (typeof low === "number") {
    return `${low}+ weeks`;
  }
  return "time estimate unavailable";
}

function formatUpskillSummary(advice: UpskillAdvice): string {
  const consultant = advice.consultant_id ? `Consultant ${advice.consultant_id}` : "Consultant";
  const role = advice.role_id ? ` for role ${advice.role_id}` : "";
  return `${consultant}${role}`;
}

function formatRankComparison(value: RankComparison): string {
  const winner = typeof value["winner_consultant_id"] === "string" ? value["winner_consultant_id"] : "unknown";
  const loser = typeof value["loser_consultant_id"] === "string" ? value["loser_consultant_id"] : "unknown";
  const decision = typeof value["decision_basis"] === "string" ? value["decision_basis"] : "comparison produced";
  return `${winner} outranks ${loser} (${decision.replace(/_/g, " ")})`;
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
            <p>{formatRankComparison(rankComparisons[0])}</p>
          )}
        </div>

        <div className="insights-column">
          <h3>Top Upskill Recommendation</h3>
          {upskillAdvice.length === 0 ? (
            <p className="insight-empty">No upskill recommendations in this run.</p>
          ) : (
            <div>
              <p>{formatUpskillSummary(upskillAdvice[0])}</p>
              {upskillAdvice[0].upskill_targets && upskillAdvice[0].upskill_targets.length > 0 ? (
                <ul>
                  {upskillAdvice[0].upskill_targets.map((target, index) => (
                    <li key={`${target.requirement}-${index}`}>
                      {target.requirement}: {toLabel(target.requirement_type, "required requirement")}, {toLabel(target.gap_status, "missing")} ({toWeeksLabel(target.estimated_weeks_low, target.estimated_weeks_high)})
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="insight-empty">No actionable skill/tool targets for this candidate.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
