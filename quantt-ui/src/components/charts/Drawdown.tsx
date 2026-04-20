import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface DataPoint {
  timestamp: string;
  drawdown_abs: number;
  drawdown_pct: number;
}

interface Props {
  data: DataPoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const abs = payload.find((p: any) => p.dataKey === "drawdown_abs");
    const pct = payload.find((p: any) => p.dataKey === "drawdown_pct");
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
        <p style={{ color: "#555", marginBottom: 4 }}>{label}</p>
        {abs && (
          <p style={{ color: "#ef4444" }}>
            Abs: <strong>{abs.value.toFixed(4)}</strong>
          </p>
        )}
        {pct && (
          <p style={{ color: "#f97316" }}>
            Pct: <strong>{pct.value.toFixed(2)}%</strong>
          </p>
        )}
      </div>
    );
  }
  return null;
};

export default function DrawdownChart({ data }: Props) {
  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.timestamp).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart
        data={formatted}
        margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
      >
        <defs>
          <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
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
          width={55}
          tickFormatter={(v) => v.toFixed(2)}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey="drawdown_abs"
          stroke="#ef4444"
          strokeWidth={2}
          fill="url(#ddGrad)"
          dot={false}
          activeDot={{ r: 4, fill: "#ef4444", stroke: "#111", strokeWidth: 2 }}
        />
        <Area
          type="monotone"
          dataKey="drawdown_pct"
          stroke="#f97316"
          strokeWidth={1.5}
          fill="none"
          dot={false}
          strokeDasharray="4 3"
          activeDot={{ r: 3, fill: "#f97316", stroke: "#111", strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
