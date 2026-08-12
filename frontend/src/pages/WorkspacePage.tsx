import { useMemo, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { RoleControls } from "@/components/controls/RoleControls";
import { PolicyPanel } from "@/components/controls/PolicyPanel";
import { AdvisoryInsightsPanel } from "@/components/ranking/AdvisoryInsightsPanel";
import { CandidateCard } from "@/components/ranking/CandidateCard";
import { ComparePanel } from "@/components/ranking/ComparePanel";
import { RunSummary } from "@/components/ranking/RunSummary";
import { useRoles } from "@/hooks/useRoles";
import { useRunRanking } from "@/hooks/useRunRanking";
import { usePolicyStore } from "@/state/usePolicyStore";

export function WorkspacePage() {
  const { policy } = usePolicyStore();
  const { data: roles = [] } = useRoles();
  const runMutation = useRunRanking();

  const [roleId, setRoleId] = useState("R-003");
  const [topN, setTopN] = useState(5);
  const [retrieveK, setRetrieveK] = useState(25);
  const [compareIds, setCompareIds] = useState<string[]>([]);

  const run = runMutation.data;

  const selectedCandidates = useMemo(() => {
    if (!run) return [];
    return run.ranked_candidates.filter((candidate) => compareIds.includes(candidate.consultant_id));
  }, [run, compareIds]);

  const onRun = () => {
    runMutation.mutate({
      roleId,
      topN,
      retrieveK,
      policy,
    });
  };

  const toggleCompare = (consultantId: string) => {
    setCompareIds((current) => {
      if (current.includes(consultantId)) {
        return current.filter((id) => id !== consultantId);
      }
      if (current.length >= 2) {
        return [current[1], consultantId];
      }
      return [...current, consultantId];
    });
  };

  return (
    <AppShell>
      <aside className="left-column">
        <RoleControls
          roles={roles}
          roleId={roleId}
          topN={topN}
          retrieveK={retrieveK}
          onRoleIdChange={setRoleId}
          onTopNChange={setTopN}
          onRetrieveKChange={setRetrieveK}
          onRun={onRun}
          isRunning={runMutation.isPending}
        />
        <PolicyPanel />
      </aside>

      <section className="right-column">
        <RunSummary run={run} />

        <section className="panel">
          <div className="panel-head">
            <h2>Ranked Shortlist</h2>
            <p>Policy-aware deterministic shortlist with explainable factors.</p>
          </div>

          {runMutation.isPending ? <p className="status-line">Generating shortlist...</p> : null}
          {runMutation.isError ? <p className="status-line error">Could not generate ranking. Check API configuration.</p> : null}

          <div className="candidate-grid">
            {(run?.ranked_candidates ?? []).map((candidate) => (
              <CandidateCard
                key={candidate.consultant_id}
                candidate={candidate}
                selected={compareIds.includes(candidate.consultant_id)}
                onToggleCompare={toggleCompare}
              />
            ))}
          </div>
        </section>

        <ComparePanel selected={selectedCandidates} />
        <AdvisoryInsightsPanel
          componentizedMode={Boolean(run?.componentized_mode)}
          rankComparisons={run?.rank_comparisons ?? []}
          upskillAdvice={run?.upskill_advice ?? []}
        />
      </section>
    </AppShell>
  );
}
