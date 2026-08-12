export function toPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function humanizeCode(value: string): string {
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function scoreClass(score: number): string {
  if (score >= 70) return "score-strong";
  if (score >= 40) return "score-medium";
  return "score-weak";
}
