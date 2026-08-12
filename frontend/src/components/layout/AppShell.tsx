import { useEffect, useState, type PropsWithChildren } from "react";

export function AppShell({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const stored = window.localStorage.getItem("ui-theme");
    if (stored === "dark" || stored === "light") {
      setTheme(stored);
      return;
    }

    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("ui-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <span className="brand-kicker">FDM Staffing Intelligence</span>
          <h1>AI Consultant Selection Assistant</h1>
        </div>
        <div className="topbar-right">
          <button type="button" className="btn-secondary theme-toggle" onClick={toggleTheme}>
            {theme === "dark" ? "Light Theme" : "Dark Theme"}
          </button>
          <p className="topbar-copy">
            Deterministic ranking with policy-controlled constraints and explainable shortlist output.
          </p>
        </div>
      </header>
      <main className="workspace-grid">{children}</main>
    </div>
  );
}
