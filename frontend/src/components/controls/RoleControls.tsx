import type { RoleOption } from "@/types/ranking";

interface RoleControlsProps {
  roles: RoleOption[];
  roleId: string;
  topN: number;
  retrieveK: number;
  onRoleIdChange: (value: string) => void;
  onTopNChange: (value: number) => void;
  onRetrieveKChange: (value: number) => void;
  onRun: () => void;
  isRunning: boolean;
}

export function RoleControls({
  roles,
  roleId,
  topN,
  retrieveK,
  onRoleIdChange,
  onTopNChange,
  onRetrieveKChange,
  onRun,
  isRunning,
}: RoleControlsProps) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Role Setup</h2>
        <p>Select a role and shortlist depth.</p>
      </div>

      <div className="form-grid">
        <label>
          Role
          <select value={roleId} onChange={(event) => onRoleIdChange(event.target.value)}>
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.id} - {role.title}
              </option>
            ))}
          </select>
        </label>

        <label>
          Top N
          <input
            type="number"
            min={3}
            max={10}
            value={topN}
            onChange={(event) => onTopNChange(Number(event.target.value))}
          />
        </label>

        <label>
          Retrieve K
          <input
            type="number"
            min={10}
            max={80}
            value={retrieveK}
            onChange={(event) => onRetrieveKChange(Number(event.target.value))}
          />
        </label>
      </div>

      <button className="btn-primary" onClick={onRun} disabled={isRunning}>
        {isRunning ? "Running Ranking..." : "Run Ranking"}
      </button>
    </section>
  );
}
