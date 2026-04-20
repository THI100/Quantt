import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface DataPoint {
  date: string;
  count: number;
}

interface Props {
  data: DataPoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
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
        <p style={{ color: "#8a5cf6" }}>
          Trades: <strong>{payload[0].value}</strong>
        </p>
      </div>
    );
  }
  return null;
};

export default function DailyTradeCountChart({ data }: Props) {
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
        <defs>
          <linearGradient id="countGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8a5cf6" stopOpacity={1} />
            <stop offset="100%" stopColor="#6d28d9" stopOpacity={0.7} />
          </linearGradient>
        </defs>
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
          width={35}
          allowDecimals={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar
          dataKey="count"
          fill="url(#countGrad)"
          radius={[3, 3, 0, 0]}
          maxBarSize={24}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
