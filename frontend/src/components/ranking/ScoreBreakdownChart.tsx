import { Bar, BarChart, Cell, ResponsiveContainer, XAxis, YAxis } from "recharts";

import type { RankedCandidate } from "@/types/ranking";

const palette = ["#176b87", "#64ccc5", "#f4b740", "#f26b38", "#2f5d50", "#5b6d5b", "#3d3d5c", "#94713f"];

interface ScoreBreakdownChartProps {
  candidate: RankedCandidate;
}

export function ScoreBreakdownChart({ candidate }: ScoreBreakdownChartProps) {
  const data = Object.entries(candidate.score_components).map(([key, value]) => ({
    key,
    value: Number(value),
  }));

  return (
    <div className="score-chart" role="img" aria-label={`Score breakdown for ${candidate.consultant_id}`}>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 8, left: 12, bottom: 4 }}>
          <XAxis type="number" domain={[0, 1]} hide />
          <YAxis dataKey="key" type="category" width={130} tick={{ fontSize: 11 }} />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {data.map((entry, index) => (
              <Cell key={entry.key} fill={palette[index % palette.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
