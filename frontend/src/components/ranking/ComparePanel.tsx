import type { RankedCandidate } from "@/types/ranking";
import { humanizeCode } from "@/utils/format";

interface ComparePanelProps {
  selected: RankedCandidate[];
}

export function ComparePanel({ selected }: ComparePanelProps) {
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
        {selected.slice(0, 2).map((candidate) => (
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
          </div>
        ))}
      </div>
    </section>
  );
}
