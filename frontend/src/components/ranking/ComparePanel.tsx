import type { RankedCandidate, UpskillAdvice } from "@/types/ranking";
import { humanizeCode } from "@/utils/format";

interface ComparePanelProps {
  selected: RankedCandidate[];
  componentizedMode: boolean;
  upskillAdvice: UpskillAdvice[];
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

export function ComparePanel({ selected, componentizedMode, upskillAdvice }: ComparePanelProps) {
  if (selected.length < 2) {
    return (
      <section className="panel compare-panel">
        <div className="panel-head">
          <h2>Candidate Compare</h2>
          <p>Select at least two candidates to compare side by side.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel compare-panel">
      <div className="panel-head">
        <h2>Candidate Compare</h2>
        <p>Direct comparison for decision review.</p>
      </div>

      <div className="compare-grid">
        {selected.slice(0, 2).map((candidate) => {
          const candidateAdvice = upskillAdvice.find((advice) => advice.consultant_id === candidate.consultant_id);

          return (
            <div key={candidate.consultant_id} className="compare-col">
              <h3>{candidate.consultant_id}</h3>
              <p className="compare-score">Fit Score {candidate.fit_score.toFixed(2)}</p>
              <ul>
                {Object.entries(candidate.score_components).map(([key, value]) => (
                  <li key={key}>
                    <span>{humanizeCode(key)}</span>
                    <strong>{(value * 100).toFixed(0)}%</strong>
                  </li>
                ))}
              </ul>

              <div className="compare-upskill">
                <h4>Upskilling Advice</h4>
                {!componentizedMode ? (
                  <p className="insight-empty">Enable componentized mode to view upskilling advice.</p>
                ) : !candidateAdvice ? (
                  <p className="insight-empty">No upskill recommendation found for this candidate.</p>
                ) : candidateAdvice.upskill_targets && candidateAdvice.upskill_targets.length > 0 ? (
                  <ul className="upskill-list">
                    {candidateAdvice.upskill_targets.map((target, index) => {
                      const priority = getTargetPriority(candidateAdvice, target.requirement);
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
            </div>
          );
        })}
      </div>
    </section>
  );
}
