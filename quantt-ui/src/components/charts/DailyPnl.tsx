import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

interface DataPoint {
  date: string;
  pnl: number;
}

interface Props {
  data: DataPoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    return (
      <div
        style={{
          background: "#111",
          border: "1px solid #2a2a2a",
          borderRadius: 8,
          padding: "8px 14px",
          fontFamily: "DM Mono, monospace",
          fontSize: 11,
          color: "#f5f0e8",
        }}
      >
        <p style={{ color: "#555", marginBottom: 2 }}>{label}</p>
        <p style={{ color: val >= 0 ? "#22c55e" : "#ef4444" }}>
          PnL:{" "}
          <strong>
            {val >= 0 ? "+" : ""}
            {val.toFixed(4)}
          </strong>
        </p>
      </div>
    );
  }
  return null;
};

export default function DailyPnlChart({ data }: Props) {
  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={formatted}
        margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
      >
        <CartesianGrid stroke="#1a1a1a" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{
            fill: "#444",
            fontSize: 10,
            fontFamily: "DM Mono, monospace",
          }}
          axisLine={false}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{
            fill: "#444",
            fontSize: 10,
            fontFamily: "DM Mono, monospace",
          }}
          axisLine={false}
          tickLine={false}
          width={55}
          tickFormatter={(v) => v.toFixed(2)}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="pnl" radius={[3, 3, 0, 0]} maxBarSize={24}>
          {formatted.map((entry, index) => (
            <Cell
              key={index}
              fill={entry.pnl >= 0 ? "#22c55e" : "#ef4444"}
              fillOpacity={0.85}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
