import React, { useState, useEffect } from "react";
import { submitReport, getReports, getBins } from "../services/api";

export default function ReportForm() {
  const [bins, setBins]           = useState([]);
  const [reports, setReports]     = useState([]);
  const [activeTab, setActiveTab] = useState("submit");
  const [loading, setLoading]     = useState(false);
  const [status, setStatus]       = useState(null);
  const [form, setForm]           = useState({
    bin_id: "BIN001", reporter: "", message: "", phone: "", fill_level: 80
  });

  useEffect(() => {
    getBins().then(res => setBins(res.data.bins || []));
    loadReports();
  }, []);

  const loadReports = () => {
    getReports().then(res => setReports(res.data.reports || []));
  };

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = () => {
    if (!form.reporter || !form.message) {
      setStatus({ type: "error", text: "Please fill in your name and message." });
      return;
    }
    setLoading(true);
    submitReport({ ...form, fill_level: parseFloat(form.fill_level) })
      .then(res => {
        setStatus({ type: "success", text: `✅ ${res.data.message}` });
        setForm({ bin_id: "BIN001", reporter: "", message: "", phone: "", fill_level: 80 });
        setLoading(false);
        loadReports();
      })
      .catch(() => {
        setStatus({ type: "error", text: "❌ Failed to submit. Try again." });
        setLoading(false);
      });
  };

  const handleSimulate = () => {
    const simReports = [
      { bin_id: "BIN003", reporter: "Emmanuel Tabi",  phone: "+237670001001", message: "Bin overflowing at Molyko Market", fill_level: 98 },
      { bin_id: "BIN006", reporter: "Grace Ndongo",   phone: "+237680002002", message: "Great Soppo bin full, waste on road", fill_level: 95 },
      { bin_id: "BIN011", reporter: "Paul Ekeme",     phone: "+237690003003", message: "Mile 16 market bin urgent", fill_level: 92 },
      { bin_id: "BIN022", reporter: "Mary Epie",      phone: "+237670004004", message: "Buea Town Hall bin almost full", fill_level: 85 },
      { bin_id: "BIN014", reporter: "Peter Nguele",   phone: "+237680005005", message: "Clerks Quarter filling fast", fill_level: 78 },
    ];
    setLoading(true);
    let count = 0;
    const submitNext = (i) => {
      if (i >= simReports.length) {
        setStatus({ type: "success", text: `✅ ${count} simulated reports submitted!` });
        setLoading(false);
        loadReports();
        return;
      }
      submitReport(simReports[i]).then(() => { count++; submitNext(i + 1); }).catch(() => submitNext(i + 1));
    };
    submitNext(0);
  };

  const inputStyle = {
    width: "100%",
    padding: "12px 14px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "16px",
    marginBottom: "14px",
    boxSizing: "border-box"
  };

  const getFillColor = (fill) => fill >= 80 ? "#e74c3c" : fill >= 60 ? "#f39c12" : "#2ecc71";

  return (
    <div>
      <h2 style={{ marginTop: 0, marginBottom: "16px", color: "#1a5276", fontSize: "18px" }}>
        📱 Community Reporting
      </h2>
      <p style={{ color: "#666", marginBottom: "16px", fontSize: "13px" }}>
        Report an overflowing bin directly from your phone.
      </p>

      {/* SUB TABS */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
        {[["submit", "📤 Report"], ["feed", `📋 Feed (${reports.length})`]].map(([key, label]) => (
          <button
            key={key}
            onClick={() => { setActiveTab(key); if (key === "feed") loadReports(); }}
            style={{
              padding: "10px 16px", border: "none", borderRadius: "8px",
              background: activeTab === key ? "#2e86c1" : "#e8f4fd",
              color: activeTab === key ? "white" : "#2e86c1",
              fontWeight: "bold", cursor: "pointer", fontSize: "13px", flex: 1
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {activeTab === "submit" && (
        <div>
          {/* FORM */}
          <div style={{
            background: "white", borderRadius: "12px",
            padding: "20px", marginBottom: "16px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ marginTop: 0, marginBottom: "16px", color: "#1a5276", fontSize: "15px" }}>
              ✍️ Submit a Report
            </h3>

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px", fontSize: "14px" }}>
              Select Bin
            </label>
            <select name="bin_id" value={form.bin_id} onChange={handleChange} style={inputStyle}>
              {bins.map(b => (
                <option key={b.bin_id} value={b.bin_id}>
                  {b.bin_id} — {b.name}
                </option>
              ))}
            </select>

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px", fontSize: "14px" }}>
              Your Name
            </label>
            <input
              name="reporter" value={form.reporter} onChange={handleChange}
              placeholder="e.g. Amara Njoku" style={inputStyle}
            />

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px", fontSize: "14px" }}>
              Phone (optional)
            </label>
            <input
              name="phone" value={form.phone} onChange={handleChange}
              placeholder="+237 6XX XXX XXX" type="tel" style={inputStyle}
            />

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px", fontSize: "14px" }}>
              Message
            </label>
            <textarea
              name="message" value={form.message} onChange={handleChange}
              placeholder="Describe the waste situation..."
              style={{ ...inputStyle, height: "80px", resize: "vertical" }}
            />

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "8px", fontSize: "14px" }}>
              Fill Level:
              <span style={{ color: getFillColor(form.fill_level), marginLeft: "8px", fontSize: "18px" }}>
                {form.fill_level}%
              </span>
            </label>
            <input
              type="range" name="fill_level" min="0" max="100"
              value={form.fill_level} onChange={handleChange}
              style={{ width: "100%", marginBottom: "16px", accentColor: getFillColor(form.fill_level) }}
            />

            {status && (
              <div style={{
                padding: "12px", borderRadius: "8px", marginBottom: "14px",
                background: status.type === "success" ? "#eafaf1" : "#fdecea",
                color: status.type === "success" ? "#1e8449" : "#e74c3c",
                border: `1px solid ${status.type === "success" ? "#2ecc71" : "#e74c3c"}`,
                fontSize: "13px"
              }}>
                {status.text}
              </div>
            )}

            <button
              onClick={handleSubmit} disabled={loading}
              style={{
                background: loading ? "#aaa" : "linear-gradient(135deg, #1a5276, #2e86c1)",
                color: "white", border: "none", padding: "14px",
                borderRadius: "8px", fontSize: "16px",
                cursor: loading ? "not-allowed" : "pointer",
                width: "100%", marginBottom: "10px"
              }}
            >
              {loading ? "⏳ Submitting..." : "📤 Submit Report"}
            </button>
          </div>

          {/* SMS SIMULATION */}
          <div style={{
            background: "white", borderRadius: "12px",
            padding: "20px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ marginTop: 0, marginBottom: "12px", color: "#1a5276", fontSize: "15px" }}>
              🤖 SMS Simulation
            </h3>
            <p style={{ color: "#666", fontSize: "13px", marginBottom: "16px" }}>
              Simulate 5 community members sending reports from Buea neighborhoods.
            </p>
            <button
              onClick={handleSimulate} disabled={loading}
              style={{
                background: loading ? "#aaa" : "linear-gradient(135deg, #1e8449, #2ecc71)",
                color: "white", border: "none", padding: "14px",
                borderRadius: "8px", fontSize: "15px",
                cursor: loading ? "not-allowed" : "pointer", width: "100%"
              }}
            >
              {loading ? "⏳ Simulating..." : "🚀 Run SMS Simulation"}
            </button>
          </div>
        </div>
      )}

      {/* REPORT FEED */}
      {activeTab === "feed" && (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ margin: 0, color: "#1a5276", fontSize: "15px" }}>📋 Report Feed</h3>
            <button
              onClick={loadReports}
              style={{
                background: "#eaf4fb", color: "#2e86c1",
                border: "1px solid #2e86c1", padding: "8px 14px",
                borderRadius: "8px", cursor: "pointer", fontSize: "13px"
              }}
            >
              🔄 Refresh
            </button>
          </div>

          {reports.length === 0
            ? <div style={{
                background: "white", borderRadius: "12px", padding: "40px",
                textAlign: "center", color: "#aaa", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
              }}>
                No reports yet. Submit one above!
              </div>
            : reports.slice().reverse().map((r, i) => (
              <div key={i} style={{
                background: "white", borderRadius: "12px", padding: "14px 16px",
                marginBottom: "10px", boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                borderLeft: `4px solid ${getFillColor(r.fill_level)}`
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "6px", marginBottom: "6px" }}>
                  <span style={{ fontWeight: "bold", fontSize: "14px" }}>📱 {r.reporter}</span>
                  <span style={{ color: "#aaa", fontSize: "11px" }}>
                    {new Date(r.timestamp).toLocaleString()}
                  </span>
                </div>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "8px" }}>
                  <span style={{
                    background: "#eaf4fb", color: "#2e86c1",
                    padding: "2px 8px", borderRadius: "10px", fontSize: "12px"
                  }}>
                    {r.bin_id}
                  </span>
                  <span style={{
                    background: getFillColor(r.fill_level), color: "white",
                    padding: "2px 8px", borderRadius: "10px", fontSize: "12px"
                  }}>
                    {r.fill_level}% full
                  </span>
                </div>
                <p style={{ margin: 0, color: "#444", fontSize: "13px" }}>💬 {r.message}</p>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}