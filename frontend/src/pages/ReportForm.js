import React, { useState, useEffect } from "react";
import { submitReport, getReports, getBins } from "../services/api";

export default function ReportForm() {
  const [bins, setBins]           = useState([]);
  const [reports, setReports]     = useState([]);
  const [activeTab, setActiveTab] = useState("submit");
  const [loading, setLoading]     = useState(false);
  const [status, setStatus]       = useState(null);
  const [form, setForm]           = useState({
    bin_id    : "BIN001",
    reporter  : "",
    message   : "",
    phone     : "",
    fill_level: 80
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
        setStatus({ type: "success", text: `✅ ${res.data.message} (${res.data.report_id})` });
        setForm({ bin_id: "BIN001", reporter: "", message: "", phone: "", fill_level: 80 });
        setLoading(false);
        loadReports();
      })
      .catch(() => {
        setStatus({ type: "error", text: "❌ Failed to submit. Is backend running?" });
        setLoading(false);
      });
  };

  // Simulate random community reports
  const handleSimulate = () => {
    const simulatedReports = [
      { bin_id: "BIN003", reporter: "Emmanuel Tabi",  phone: "+237670001001", message: "Bin overflowing at Molyko Market, very bad smell",       fill_level: 98 },
      { bin_id: "BIN006", reporter: "Grace Ndongo",   phone: "+237680002002", message: "Great Soppo bin full, waste spilling on the road",        fill_level: 95 },
      { bin_id: "BIN011", reporter: "Paul Ekeme",     phone: "+237690003003", message: "Mile 16 market bin needs urgent collection",              fill_level: 92 },
      { bin_id: "BIN022", reporter: "Mary Epie",      phone: "+237670004004", message: "Buea Town Hall bin is almost full",                       fill_level: 85 },
      { bin_id: "BIN014", reporter: "Peter Nguele",   phone: "+237680005005", message: "Clerks Quarter bin filling up fast today",                fill_level: 78 },
    ];

    setLoading(true);
    let count = 0;

    const submitNext = (i) => {
      if (i >= simulatedReports.length) {
        setStatus({ type: "success", text: `✅ ${count} simulated reports submitted successfully!` });
        setLoading(false);
        loadReports();
        return;
      }
      submitReport(simulatedReports[i])
        .then(() => { count++; submitNext(i + 1); })
        .catch(() => submitNext(i + 1));
    };

    submitNext(0);
  };

  const inputStyle = {
    width: "100%", padding: "10px 14px", borderRadius: "8px",
    border: "1px solid #ccc", fontSize: "14px", marginBottom: "16px",
    boxSizing: "border-box"
  };

  const getFillColor = (fill) =>
    fill >= 80 ? "#e74c3c" : fill >= 60 ? "#f39c12" : "#2ecc71";

  return (
    <div>
      <h2 style={{ marginTop: 0, color: "#1a5276" }}>📱 Community Reporting</h2>
      <p style={{ color: "#666", marginBottom: "20px" }}>
        Simulate SMS/WhatsApp waste reports from Buea community members.
      </p>

      {/* SUB TABS */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
        {[["submit", "📤 Submit Report"], ["feed", `📋 Report Feed (${reports.length})`]].map(([key, label]) => (
          <button
            key={key}
            onClick={() => { setActiveTab(key); if (key === "feed") loadReports(); }}
            style={{
              padding: "10px 20px", border: "none", borderRadius: "8px",
              background: activeTab === key ? "#2e86c1" : "#e8f4fd",
              color: activeTab === key ? "white" : "#2e86c1",
              fontWeight: "bold", cursor: "pointer", fontSize: "14px"
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* SUBMIT TAB */}
      {activeTab === "submit" && (
        <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>

          {/* FORM */}
          <div style={{
            background: "white", borderRadius: "12px", padding: "28px",
            flex: 1, minWidth: "300px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ marginTop: 0, color: "#1a5276" }}>✍️ Manual Report</h3>

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px" }}>Select Bin</label>
            <select name="bin_id" value={form.bin_id} onChange={handleChange} style={inputStyle}>
              {bins.map(b => (
                <option key={b.bin_id} value={b.bin_id}>
                  {b.bin_id} — {b.name} ({b.neighborhood})
                </option>
              ))}
            </select>

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px" }}>Your Name</label>
            <input
              name="reporter" value={form.reporter} onChange={handleChange}
              placeholder="e.g. Amara Njoku" style={inputStyle}
            />

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px" }}>
              Phone <span style={{ color: "#aaa", fontWeight: "normal" }}>(optional)</span>
            </label>
            <input
              name="phone" value={form.phone} onChange={handleChange}
              placeholder="+237 6XX XXX XXX" style={inputStyle}
            />

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "6px" }}>Message</label>
            <textarea
              name="message" value={form.message} onChange={handleChange}
              placeholder="Describe the waste situation..."
              style={{ ...inputStyle, height: "90px", resize: "vertical" }}
            />

            <label style={{ fontWeight: "bold", display: "block", marginBottom: "8px" }}>
              Estimated Fill Level:
              <span style={{
                color: getFillColor(form.fill_level),
                fontWeight: "bold", marginLeft: "8px", fontSize: "18px"
              }}>
                {form.fill_level}%
              </span>
            </label>
            <input
              type="range" name="fill_level" min="0" max="100"
              value={form.fill_level} onChange={handleChange}
              style={{ width: "100%", marginBottom: "20px", accentColor: getFillColor(form.fill_level) }}
            />

            {status && (
              <div style={{
                padding: "12px 16px", borderRadius: "8px", marginBottom: "16px",
                background: status.type === "success" ? "#eafaf1" : "#fdecea",
                color: status.type === "success" ? "#1e8449" : "#e74c3c",
                border: `1px solid ${status.type === "success" ? "#2ecc71" : "#e74c3c"}`
              }}>
                {status.text}
              </div>
            )}

            <button
              onClick={handleSubmit} disabled={loading}
              style={{
                background: loading ? "#aaa" : "linear-gradient(135deg, #1a5276, #2e86c1)",
                color: "white", border: "none", padding: "14px",
                borderRadius: "8px", fontSize: "15px",
                cursor: loading ? "not-allowed" : "pointer", width: "100%",
                marginBottom: "12px"
              }}
            >
              {loading ? "⏳ Submitting..." : "📤 Submit Report"}
            </button>
          </div>

          {/* SIMULATION PANEL */}
          <div style={{
            background: "white", borderRadius: "12px", padding: "28px",
            flex: 1, minWidth: "300px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ marginTop: 0, color: "#1a5276" }}>🤖 SMS Simulation</h3>
            <p style={{ color: "#666", fontSize: "14px" }}>
              Simulate 5 community members sending WhatsApp/SMS reports
              from different neighborhoods in Buea.
            </p>

            <div style={{ background: "#f8f9fa", borderRadius: "8px", padding: "16px", marginBottom: "20px" }}>
              {[
                ["Emmanuel Tabi",  "BIN003 — Molyko Market",     "98%"],
                ["Grace Ndongo",   "BIN006 — Great Soppo",        "95%"],
                ["Paul Ekeme",     "BIN011 — Mile 16 Market",     "92%"],
                ["Mary Epie",      "BIN022 — Buea Town Hall",     "85%"],
                ["Peter Nguele",   "BIN014 — Clerks Quarter",     "78%"],
              ].map(([name, bin, fill], i) => (
                <div key={i} style={{
                  display: "flex", justifyContent: "space-between",
                  padding: "8px 0", borderBottom: i < 4 ? "1px solid #eee" : "none",
                  fontSize: "13px"
                }}>
                  <span>📱 <strong>{name}</strong></span>
                  <span style={{ color: "#666" }}>{bin}</span>
                  <span style={{
                    color: "white", background: getFillColor(parseInt(fill)),
                    padding: "2px 8px", borderRadius: "10px", fontSize: "12px"
                  }}>
                    {fill}
                  </span>
                </div>
              ))}
            </div>

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

      {/* FEED TAB */}
      {activeTab === "feed" && (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ margin: 0, color: "#1a5276" }}>📋 Community Report Feed</h3>
            <button
              onClick={loadReports}
              style={{
                background: "#eaf4fb", color: "#2e86c1", border: "1px solid #2e86c1",
                padding: "8px 16px", borderRadius: "8px", cursor: "pointer", fontSize: "13px"
              }}
            >
              🔄 Refresh
            </button>
          </div>

          {reports.length === 0
            ? (
              <div style={{
                background: "white", borderRadius: "12px", padding: "40px",
                textAlign: "center", color: "#aaa", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
              }}>
                No reports yet. Submit one or run the simulation!
              </div>
            )
            : reports.slice().reverse().map((r, i) => (
              <div key={i} style={{
                background: "white", borderRadius: "12px", padding: "16px 20px",
                marginBottom: "12px", boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                borderLeft: `4px solid ${getFillColor(r.fill_level)}`
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                  <div>
                    <span style={{ fontWeight: "bold", fontSize: "15px" }}>📱 {r.reporter}</span>
                    <span style={{
                      marginLeft: "10px", background: "#eaf4fb", color: "#2e86c1",
                      padding: "2px 10px", borderRadius: "10px", fontSize: "12px"
                    }}>
                      {r.bin_id}
                    </span>
                    <span style={{
                      marginLeft: "8px", background: getFillColor(r.fill_level),
                      color: "white", padding: "2px 10px", borderRadius: "10px", fontSize: "12px"
                    }}>
                      {r.fill_level}% full
                    </span>
                  </div>
                  <span style={{ color: "#aaa", fontSize: "12px" }}>
                    {new Date(r.timestamp).toLocaleString()}
                  </span>
                </div>
                <p style={{ margin: "0", color: "#444", fontSize: "14px" }}>💬 {r.message}</p>
                {r.phone !== "N/A" && (
                  <p style={{ margin: "6px 0 0", color: "#aaa", fontSize: "12px" }}>📞 {r.phone}</p>
                )}
                <div style={{ marginTop: "8px" }}>
                  <span style={{
                    background: "#eafaf1", color: "#1e8449",
                    padding: "2px 10px", borderRadius: "10px", fontSize: "12px"
                  }}>
                    ✅ {r.report_id} — {r.status}
                  </span>
                </div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}