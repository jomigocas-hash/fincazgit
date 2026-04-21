"use client";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const COLORS = ["#3b82f6", "#6366f1", "#8b5cf6", "#a78bfa"];

export default function MarketChart({ data }) {
  if (!data || data.length === 0) return null;

  const top10 = [...data].slice(0, 10);

  const fmt = (v) => "$" + (v / 1_000_000).toFixed(1) + "M";

  return (
    <div className="bg-slate-800 rounded-xl p-4 mb-6">
      <h2 className="text-white font-semibold mb-4 text-sm">
        Precio/m² por barrio (Top 10)
      </h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={top10} layout="vertical" margin={{ left: 10, right: 30 }}>
          <XAxis type="number" tickFormatter={fmt} tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <YAxis
            type="category"
            dataKey="neighborhood"
            width={140}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
          />
          <Tooltip
            formatter={(v) => ["$" + Number(v).toLocaleString("es-CO"), "Precio/m²"]}
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
            labelStyle={{ color: "#fff", fontWeight: "bold", marginBottom: 4 }}
            itemStyle={{ color: "#93c5fd" }}
          />
          <Bar dataKey="avg_price_per_m2" radius={[0, 4, 4, 0]}>
            {top10.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
