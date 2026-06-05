import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { getPredictions } from "../services/api";

const StatCard = ({ title, value, color, icon }) => (
  <div style={{
    background: "white", borderRadius: "12px", padding: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)", borderLeft: `5px solid ${color}`,
    minWidth: "180px", flex: 1
  }}>
    <div style={{ fontSize: "28px" }}>{icon}</div>
    <div style={{ fontSize: "32px", fontWeight: "bold", color }}>{value}</div>
    <div style={{ fontSize: "13px", color: "#666", marginTop: "4px" }}>{title}</div>
  </div>
);

export default function Dashboard() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);

  useEffect(() => {
    getPredictions()
      .then(res => {
        setPredictions(res.data.predictions || []);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to load predictions. Is the backend running?");
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ textAlign: "center", padding: "40px" }}>⏳ Loading predictions...</div>;
  if (error)   return <div style={{ color: "red", padding: "20px" }}>❌ {error}</div>;

  const needsCollection = predictions.filter(p => p.needs_collection);
  const avgFill = predictions.length
    ? (predictions.reduce((s, p) => s + p.predicted_fill, 0) / predictions.length).toFixed(1)
    : 0;

  // Group by neighborhood
  const byNeighborhood = {};
  predictions.forEach(p => {
    if (!byNeighborhood[p.neighborhood]) {
      byNeighborhood[p.neighborhood] = { total: 0, count: 0 };
    }
    byNeighborhood[p.neighborhood].total += p.predicted_fill;
    byNeighborhood[p.neighborhood].count += 1;
  });

  const chartData = Object.entries(byNeighborhood).map(([name, val]) => ({
    name,
    avg_fill: parseFloat((val.total / val.count).toFixed(1))
  })).sort((a, b) => b.avg_fill - a.avg_fill);

  const getColor = (fill) => fill >= 80 ? "#e74c3c" : fill >= 60 ? "#f39c12" : "#2ecc71";

  return (
    <div>
      <h2 style={{ marginTop: 0, color: "#1a5276" }}>📊 Dashboard</h2>

      {/* STAT CARDS */}
      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", marginBottom: "32px" }}>
        <StatCard title="Total Bins"          value={predictions.length}      color="#2e86c1" icon="🗑️" />
        <StatCard title="Need Collection"     value={needsCollection.length}  color="#e74c3c" icon="🚨" />
        <StatCard title="Avg Fill Level"      value={`${avgFill}%`}           color="#f39c12" icon="📈" />
        <StatCard title="Operational Trucks"  value="3"                       color="#2ecc71" icon="🚛" />
      </div>

      {/* BAR CHART */}
      <div style={{ background: "white", borderRadius: "12px", padding: "24px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", marginBottom: "32px" }}>
        <h3 style={{ marginTop: 0, color: "#1a5276" }}>Average Fill Level by Neighborhood</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
            <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} />
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
      <div style={{ background: "white", borderRadius: "12px", padding: "24px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}>
        <h3 style={{ marginTop: 0, color: "#1a5276" }}>🚨 Bins Needing Collection</h3>
        {needsCollection.length === 0
          ? <p style={{ color: "#2ecc71" }}>✅ All bins are within acceptable levels!</p>
          : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
              <thead>
                <tr style={{ background: "#eaf4fb" }}>
                  {["Bin ID", "Name", "Neighborhood", "Fill %", "Status"].map(h => (
                    <th key={h} style={{ padding: "10px", textAlign: "left", borderBottom: "2px solid #ddd" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {needsCollection.map((bin, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "10px" }}>{bin.bin_id}</td>
                    <td style={{ padding: "10px" }}>{bin.name}</td>
                    <td style={{ padding: "10px" }}>{bin.neighborhood}</td>
                    <td style={{ padding: "10px" }}>
                      <span style={{
                        background: getColor(bin.predicted_fill),
                        color: "white", padding: "3px 10px",
                        borderRadius: "12px", fontWeight: "bold"
                      }}>
                        {bin.predicted_fill}%
                      </span>
                    </td>
                    <td style={{ padding: "10px" }}>
                      {bin.is_market_area ? "🏪 Market Area" : "🏘️ Residential"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        }
      </div>
    </div>
  );
}