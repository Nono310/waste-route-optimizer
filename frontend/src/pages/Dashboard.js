import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";


const StatCard = ({ title, value, color, icon }) => (
  <div style={{
    background: "white",
    borderRadius: "12px",
    padding: "14px 16px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    borderLeft: `5px solid ${color}`,
    flex: 1,
    minWidth: "140px"
  }}>
    <div style={{ fontSize: "22px" }}>{icon}</div>
    <div style={{ fontSize: "26px", fontWeight: "bold", color }}>{value}</div>
    <div style={{ fontSize: "12px", color: "#666", marginTop: "2px" }}>{title}</div>
  </div>
);

export default function Dashboard({ predictions = [], loading = false }) {
  const [error] = useState(null);
  if (loading) return <div style={{ textAlign: "center", padding: "40px" }}>⏳ Loading...</div>;
  if (error)   return <div style={{ color: "red", padding: "20px" }}>❌ {error}</div>;

  const needsCollection = predictions.filter(p => p.needs_collection);
  const avgFill = predictions.length
    ? (predictions.reduce((s, p) => s + p.predicted_fill, 0) / predictions.length).toFixed(1)
    : 0;

  const byNeighborhood = {};
  predictions.forEach(p => {
    if (!byNeighborhood[p.neighborhood]) byNeighborhood[p.neighborhood] = { total: 0, count: 0 };
    byNeighborhood[p.neighborhood].total += p.predicted_fill;
    byNeighborhood[p.neighborhood].count += 1;
  });

  const chartData = Object.entries(byNeighborhood)
    .map(([name, val]) => ({ name, avg_fill: parseFloat((val.total / val.count).toFixed(1)) }))
    .sort((a, b) => b.avg_fill - a.avg_fill);

  const getColor = (fill) => fill >= 80 ? "#e74c3c" : fill >= 60 ? "#f39c12" : "#2ecc71";

  return (
    <div>
      <h2 style={{ marginTop: 0, marginBottom: "16px", color: "#1a5276", fontSize: "18px" }}>
        📊 Dashboard
      </h2>

      {/* STAT CARDS */}
      <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", marginBottom: "20px" }}>
        <StatCard title="Total Bins"       value={predictions.length}     color="#2e86c1" icon="🗑️" />
        <StatCard title="Need Collection"  value={needsCollection.length} color="#e74c3c" icon="🚨" />
        <StatCard title="Avg Fill Level"   value={`${avgFill}%`}          color="#f39c12" icon="📈" />
        <StatCard title="Trucks Available" value="3"                      color="#2ecc71" icon="🚛" />
      </div>

      {/* BAR CHART */}
      <div style={{
        background: "white", borderRadius: "12px",
        padding: "16px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        marginBottom: "20px", overflowX: "auto"
      }}>
        <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#1a5276", fontSize: "15px" }}>
          Fill Level by Neighborhood
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={55} />
            <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} />
            <Tooltip formatter={(v) => [`${v}%`, "Avg Fill"]} />
            <Bar dataKey="avg_fill" radius={[6, 6, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={getColor(entry.avg_fill)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* BIN TABLE */}
      <div style={{
        background: "white", borderRadius: "12px",
        padding: "16px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        overflowX: "auto"
      }}>
        <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#1a5276", fontSize: "15px" }}>
          🚨 Bins Needing Collection
        </h3>
        {needsCollection.length === 0
          ? <p style={{ color: "#2ecc71" }}>✅ All bins within acceptable levels!</p>
          : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                <thead>
                  <tr style={{ background: "#eaf4fb" }}>
                    {["Bin ID", "Name", "Area", "Fill %"].map(h => (
                      <th key={h} style={{ padding: "8px", textAlign: "left", borderBottom: "2px solid #ddd", whiteSpace: "nowrap" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {needsCollection.map((bin, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: "8px", whiteSpace: "nowrap" }}>{bin.bin_id}</td>
                      <td style={{ padding: "8px" }}>{bin.name}</td>
                      <td style={{ padding: "8px", whiteSpace: "nowrap" }}>{bin.neighborhood}</td>
                      <td style={{ padding: "8px" }}>
                        <span style={{
                          background: getColor(bin.predicted_fill),
                          color: "white", padding: "2px 8px",
                          borderRadius: "12px", fontWeight: "bold",
                          whiteSpace: "nowrap"
                        }}>
                          {bin.predicted_fill}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        }
      </div>
    </div>
  );
}