import type { PropsWithChildren } from "react";

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <span className="brand-kicker">FDM Staffing Intelligence</span>
          <h1>AI Consultant Selection Assistant</h1>
        </div>
        <p className="topbar-copy">
          Deterministic ranking with policy-controlled constraints and explainable shortlist output.
        </p>
      </header>
      <main className="workspace-grid">{children}</main>
    </div>
  );
}
