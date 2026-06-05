import React, { useState } from "react";
import { getOptimizedRoutes } from "../services/api";

export default function Routes() {
  const [routes, setRoutes]   = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleOptimize = () => {
    setLoading(true);
    setError(null);
    getOptimizedRoutes()
      .then(res => {
        setRoutes(res.data.routes || []);
        setSummary({
          bins    : res.data.bins_to_collect,
          trucks  : res.data.trucks_used,
          distance: res.data.total_distance_km
        });
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to get routes. Is the backend running?");
        setLoading(false);
      });
  };

  const TRUCK_COLORS = ["#2e86c1", "#e74c3c", "#2ecc71", "#f39c12"];

  return (
    <div>
      <h2 style={{ marginTop: 0, color: "#1a5276" }}>🚛 Optimized Collection Routes</h2>

      <button
        onClick={handleOptimize}
        disabled={loading}
        style={{
          background: loading ? "#aaa" : "linear-gradient(135deg, #1a5276, #2e86c1)",
          color: "white", border: "none", padding: "14px 32px",
          borderRadius: "8px", fontSize: "16px", cursor: loading ? "not-allowed" : "pointer",
          marginBottom: "24px", boxShadow: "0 2px 6px rgba(0,0,0,0.2)"
        }}
      >
        {loading ? "⏳ Optimizing routes..." : "🧬 Run Route Optimization"}
      </button>

      {error && <div style={{ color: "red", marginBottom: "16px" }}>❌ {error}</div>}

      {summary && (
        <div style={{ display: "flex", gap: "16px", marginBottom: "24px", flexWrap: "wrap" }}>
          {[
            ["Bins to Collect", summary.bins,              "#e74c3c", "🗑️"],
            ["Trucks Needed",   summary.trucks,            "#2e86c1", "🚛"],
            ["Total Distance",  `${summary.distance} km`,  "#2ecc71", "📍"],
          ].map(([title, value, color, icon]) => (
            <div key={title} style={{
              background: "white", borderRadius: "12px", padding: "16px 24px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)", borderLeft: `5px solid ${color}`, flex: 1
            }}>
              <div style={{ fontSize: "24px" }}>{icon}</div>
              <div style={{ fontSize: "28px", fontWeight: "bold", color }}>{value}</div>
              <div style={{ fontSize: "13px", color: "#666" }}>{title}</div>
            </div>
          ))}
        </div>
      )}

      {routes.map((route, i) => (
        <div key={i} style={{
          background: "white", borderRadius: "12px", padding: "20px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)", marginBottom: "16px",
          borderTop: `4px solid ${TRUCK_COLORS[i % TRUCK_COLORS.length]}`
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ margin: 0, color: TRUCK_COLORS[i % TRUCK_COLORS.length] }}>
              🚛 {route.truck_id}
            </h3>
            <div style={{ display: "flex", gap: "16px", fontSize: "13px", color: "#666" }}>
              <span>📦 {route.total_load_kg} kg</span>
              <span>📍 {route.distance_km} km</span>
              <span>🗑️ {route.total_bins} bins</span>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
            <span style={{ background: "#1a5276", color: "white", padding: "6px 12px", borderRadius: "20px", fontSize: "13px" }}>
              🏭 Depot
            </span>
            {route.stops.map((stop, j) => (
              <React.Fragment key={j}>
                <span style={{ color: "#aaa", fontSize: "18px" }}>→</span>
                <div style={{
                  background: stop.fill_percentage >= 80 ? "#fdecea" : "#eaf4fb",
                  border: `1px solid ${stop.fill_percentage >= 80 ? "#e74c3c" : "#2e86c1"}`,
                  borderRadius: "8px", padding: "6px 12px", fontSize: "12px"
                }}>
                  <div style={{ fontWeight: "bold" }}>{stop.name}</div>
                  <div style={{ color: "#666" }}>{stop.fill_percentage}% full</div>
                </div>
              </React.Fragment>
            ))}
            <span style={{ color: "#aaa", fontSize: "18px" }}>→</span>
            <span style={{ background: "#1a5276", color: "white", padding: "6px 12px", borderRadius: "20px", fontSize: "13px" }}>
              🏭 Depot
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}