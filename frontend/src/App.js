import React, { useState } from "react";
import Dashboard from "./pages/Dashboard";
import MapView from "./pages/MapView";
import Routes from "./pages/Routes";
import ReportForm from "./pages/ReportForm";
import "./App.css";

const TABS = ["Dashboard", "Map", "Routes", "Report"];

export default function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");

  return (
    <div style={{ fontFamily: "Arial, sans-serif", minHeight: "100vh", background: "#f0f4f8" }}>
      {/* HEADER */}
      <div style={{
        background: "linear-gradient(135deg, #1a5276, #2e86c1)",
        color: "white",
        padding: "16px 24px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
      }}>
        <h1 style={{ margin: 0, fontSize: "20px" }}>
          🗑️ AI Waste Route Optimizer — Buea, Cameroon
        </h1>
        <p style={{ margin: "4px 0 0", fontSize: "13px", opacity: 0.85 }}>
          University of Buea · MBARGA MBOM NOEMIE
        </p>
      </div>

      {/* TABS */}
      <div style={{ background: "white", borderBottom: "2px solid #2e86c1", display: "flex" }}>
        {TABS.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "12px 24px",
              border: "none",
              background: activeTab === tab ? "#2e86c1" : "white",
              color: activeTab === tab ? "white" : "#333",
              fontWeight: activeTab === tab ? "bold" : "normal",
              cursor: "pointer",
              fontSize: "14px",
              borderBottom: activeTab === tab ? "3px solid #1a5276" : "none"
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <div style={{ padding: "24px" }}>
        {activeTab === "Dashboard" && <Dashboard />}
        {activeTab === "Map"       && <MapView />}
        {activeTab === "Routes"    && <Routes />}
        {activeTab === "Report"    && <ReportForm />}
      </div>
    </div>
  );
}