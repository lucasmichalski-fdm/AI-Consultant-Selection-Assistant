import { policyLabels } from "@/services/rankingService";
import { usePolicyStore } from "@/state/usePolicyStore";
import type { PolicyMode } from "@/types/ranking";

const modeFields = [
  "locationMode",
  "startDateMode",
  "authorizationMode",
  "experienceMode",
  "certificationMode",
  "domainMode",
] as const;

const boolFields = ["enforceOfficeSchedule", "allowRelocationPath"] as const;

const modes: PolicyMode[] = ["hard", "soft", "ignore"];

export function PolicyPanel() {
  const { policy, setMode, setFlag, reset } = usePolicyStore();

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Decision Policy</h2>
        <p>Control which constraints are hard blockers versus soft factors.</p>
      </div>

      <div className="policy-stack">
        {modeFields.map((field) => (
          <div key={field} className="policy-row">
            <span>{policyLabels[field]}</span>
            <div className="chip-group">
              {modes.map((mode) => (
                <button
                  key={mode}
                  className={policy[field] === mode ? "chip active" : "chip"}
                  onClick={() => setMode(field, mode)}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
        ))}

        {boolFields.map((field) => (
          <label key={field} className="toggle-row">
            <input
              type="checkbox"
              checked={policy[field]}
              onChange={(event) => setFlag(field, event.target.checked)}
            />
            <span>{policyLabels[field]}</span>
          </label>
        ))}
      </div>

      <button className="btn-secondary" onClick={reset}>
        Reset Policy
      </button>
    </section>
  );
}
