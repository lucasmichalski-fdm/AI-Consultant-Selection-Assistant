import type { RankedCandidate, UpskillAdvice } from "@/types/ranking";

interface AdvisoryInsightsPanelProps {
  componentizedMode: boolean;
  upskillAdvice: UpskillAdvice[];
  selectedCandidates: RankedCandidate[];
}

function formatUpskillSummary(advice: UpskillAdvice): string {
  const consultant = advice.consultant_id ? `Consultant ${advice.consultant_id}` : "Consultant";
  const role = advice.role_id ? ` for role ${advice.role_id}` : "";
  return `${consultant}${role}`;
}

type PriorityLevel = "high" | "medium" | "low";

function normalizeTerm(term: string | undefined): string {
  return (term ?? "").trim().toLowerCase();
}

function getTargetPriority(advice: UpskillAdvice, requirement: string): PriorityLevel {
  const normalized = normalizeTerm(requirement);
  const matchingGap = advice.requirement_gaps?.find((gap) => normalizeTerm(gap.requirement) === normalized);

  if (!matchingGap) {
    return "medium";
  }

  if (matchingGap.mandatory === false) {
    return "low";
  }

  if (matchingGap.gap_status === "missing") {
    return "high";
  }

  if (matchingGap.gap_status === "development_opportunity") {
    return "medium";
  }

  if (matchingGap.gap_status === "unverified") {
    return "low";
  }

  return "medium";
}

function getPriorityLabel(priority: PriorityLevel): string {
  if (priority === "high") return "High priority";
  if (priority === "low") return "Lower priority";
  return "Medium priority";
}

export function AdvisoryInsightsPanel({
  componentizedMode,
  upskillAdvice,
  selectedCandidates,
}: AdvisoryInsightsPanelProps) {
  const highestRankedSelected = selectedCandidates
    .slice()
    .sort((a, b) => a.rank - b.rank)[0];

  const selectedAdvice = highestRankedSelected
    ? upskillAdvice.find((advice) => advice.consultant_id === highestRankedSelected.consultant_id)
    : undefined;

  if (!componentizedMode) {
    return (
      <section className="panel advisory-panel">
        <div className="panel-head">
          <h2>Upskilling Advice</h2>
          <p>Enable componentized mode on the backend to emit comparisons and upskill recommendations.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel advisory-panel">
      <div className="panel-head">
        <h2>Upskilling Advice</h2>
        <p>Displays advice for the highest-ranked consultant currently selected for comparison.</p>
      </div>

      <div className="insights-column">
        <h3>Selected Candidate Recommendation</h3>
        {selectedCandidates.length === 0 ? (
          <p className="insight-empty">Select candidates in the shortlist to view targeted upskilling advice.</p>
        ) : !highestRankedSelected ? (
          <p className="insight-empty">No selected candidate available for upskilling advice.</p>
        ) : !selectedAdvice ? (
          <p className="insight-empty">No upskill recommendation found for consultant {highestRankedSelected.consultant_id}.</p>
        ) : (
          <div>
            <p>{formatUpskillSummary(selectedAdvice)}</p>
            {selectedAdvice.upskill_targets && selectedAdvice.upskill_targets.length > 0 ? (
              <ul className="upskill-list">
                {selectedAdvice.upskill_targets.map((target, index) => {
                  const priority = getTargetPriority(selectedAdvice, target.requirement);
                  return (
                    <li key={`${target.requirement}-${index}`} className="upskill-list-item">
                      <span className="upskill-name">{target.requirement}</span>
                      <span className={`priority-tag priority-${priority}`}>{getPriorityLabel(priority)}</span>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="insight-empty">No actionable skill/tool targets for this candidate.</p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
