import type { RankingRunResponse } from "@/types/ranking";

interface RunSummaryProps {
  run: RankingRunResponse | undefined;
}

export function RunSummary({ run }: RunSummaryProps) {
  if (!run) {
    return (
      <section className="panel">
        <div className="panel-head">
          <h2>Run Summary</h2>
          <p>Run ranking to generate shortlist insights.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Run Summary</h2>
        <p>Request {run.request_id}</p>
      </div>

      <div className="summary-grid">
        <div>
          <span>Role</span>
          <strong>{run.role_id}</strong>
        </div>
        <div>
          <span>Total Candidates</span>
          <strong>{run.total_candidates}</strong>
        </div>
        <div>
          <span>Retrieved K</span>
          <strong>{run.retrieved_k}</strong>
        </div>
        <div>
          <span>Top N</span>
          <strong>{run.top_n}</strong>
        </div>
        <div>
          <span>Generated</span>
          <strong>{new Date(run.generated_at).toLocaleTimeString()}</strong>
        </div>
        <div>
          <span>Pipeline</span>
          <strong>{run.componentized_mode ? "Componentized" : "Classic"}</strong>
        </div>
      </div>
    </section>
  );
}
