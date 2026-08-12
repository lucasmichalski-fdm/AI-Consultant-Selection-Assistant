import clsx from "clsx";

import type { RankedCandidate } from "@/types/ranking";
import { humanizeCode, scoreClass } from "@/utils/format";
import { ScoreBreakdownChart } from "@/components/ranking/ScoreBreakdownChart";

interface CandidateCardProps {
  candidate: RankedCandidate;
  selected: boolean;
  onToggleCompare: (consultantId: string) => void;
}

export function CandidateCard({ candidate, selected, onToggleCompare }: CandidateCardProps) {
  return (
    <article className={clsx("candidate-card", scoreClass(candidate.fit_score), selected && "selected") }>
      <header className="candidate-head">
        <div>
          <p className="rank-pill">Rank {candidate.rank}</p>
          <h3>{candidate.consultant_id}</h3>
          <p className="status-line">
            Eligibility: {candidate.eligibility_status ?? "unknown"}
            {typeof candidate.ranking_tier === "number" ? ` | Tier ${candidate.ranking_tier}` : ""}
          </p>
        </div>
        <div className="fit-score">{candidate.fit_score.toFixed(2)}</div>
      </header>

      <ScoreBreakdownChart candidate={candidate} />

      <div className="candidate-meta">
        <div>
          <h4>Reason Codes</h4>
          <div className="tag-wrap">
            {candidate.reason_codes.map((reason) => (
              <span key={reason} className="tag neutral">
                {humanizeCode(reason)}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h4>Risk Flags</h4>
          <div className="tag-wrap">
            {candidate.risk_flags.length === 0 ? (
              <span className="tag good">No risk flags</span>
            ) : (
              candidate.risk_flags.map((risk) => (
                <span key={risk} className="tag warn">
                  {humanizeCode(risk)}
                </span>
              ))
            )}
          </div>
        </div>
      </div>

      <button className="btn-secondary" onClick={() => onToggleCompare(candidate.consultant_id)}>
        {selected ? "Remove from Compare" : "Add to Compare"}
      </button>
    </article>
  );
}
