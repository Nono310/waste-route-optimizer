import React, { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import MapView from "./pages/MapView";
import Routes from "./pages/Routes";
import ReportForm from "./pages/ReportForm";
import { getPredictions } from "./services/api";
import "./App.css";

const TABS = [
  { id: "Dashboard", icon: "📊" },
  { id: "Map", icon: "🗺️" },
  { id: "Routes", icon: "🚛" },
  { id: "Report", icon: "📱" }
];

export default function App() {
  const [activeTab, setActiveTab]       = useState("Dashboard");
  const [predictions, setPredictions]   = useState([]);
  const [loadingPreds, setLoadingPreds] = useState(true);

  // Load predictions once at app level and share across all tabs
  useEffect(() => {
    const fetchPreds = () => {
      getPredictions()
        .then(res => {
          setPredictions(res.data.predictions || []);
          setLoadingPreds(false);
        })
        .catch(() => setLoadingPreds(false));
    };
    fetchPreds();
    // Refresh every 30 seconds
    const interval = setInterval(fetchPreds, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ fontFamily: "Arial, sans-serif", minHeight: "100vh", background: "#f0f4f8" }}>

      {/* HEADER */}
      <div style={{
        background: "linear-gradient(135deg, #1a5276, #2e86c1)",
        color: "white",
        padding: "12px 16px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
      }}>
        <h1 style={{ margin: 0, fontSize: "16px", fontWeight: "bold" }}>
          🗑️ AI Waste Route Optimizer
        </h1>
        <p style={{ margin: "2px 0 0", fontSize: "11px", opacity: 0.85 }}>
          Buea, Cameroon · University of Buea
          {loadingPreds && <span style={{ marginLeft: "8px", opacity: 0.7 }}>⏳ Loading...</span>}
        </p>
      </div>

      {/* TABS */}
      <div style={{
        background: "white",
        borderBottom: "2px solid #2e86c1",
        display: "flex",
        overflowX: "auto",
        WebkitOverflowScrolling: "touch",
        scrollbarWidth: "none"
      }}>
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "12px 20px",
              border: "none",
              background: activeTab === tab.id ? "#2e86c1" : "white",
              color: activeTab === tab.id ? "white" : "#333",
              fontWeight: activeTab === tab.id ? "bold" : "normal",
              cursor: "pointer",
              fontSize: "13px",
              whiteSpace: "nowrap",
              borderBottom: activeTab === tab.id ? "3px solid #1a5276" : "none",
              flexShrink: 0
            }}
          >
            {tab.icon} {tab.id}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <div style={{ padding: "16px" }}>
        {activeTab === "Dashboard" && <Dashboard predictions={predictions} loading={loadingPreds} />}
        {activeTab === "Map"       && <MapView predictions={predictions} loading={loadingPreds} />}
        {activeTab === "Routes"    && <Routes />}
        {activeTab === "Report"    && <ReportForm />}
      </div>
    </div>
  );
}