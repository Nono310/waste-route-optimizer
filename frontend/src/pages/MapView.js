import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, Marker } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getPredictions, getOptimizedRoutes } from "../services/api";

// Fix leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl       : "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl     : "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const DEPOT    = [4.1534, 9.2916];
const COLORS   = ["#2e86c1", "#e74c3c", "#2ecc71", "#f39c12"];

const getBinColor = (fill) =>
  fill >= 80 ? "#e74c3c" : fill >= 60 ? "#f39c12" : "#2ecc71";

export default function MapView() {
  const [predictions, setPredictions] = useState([]);
  const [routes, setRoutes]           = useState([]);
  const [showRoutes, setShowRoutes]   = useState(false);
  const [loading, setLoading]         = useState(true);
  const [routeLoading, setRouteLoading] = useState(false);

  const fetchPredictions = () => {
    getPredictions()
      .then(res => {
        setPredictions(res.data.predictions || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(fetchPredictions, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLoadRoutes = () => {
    setRouteLoading(true);
    getOptimizedRoutes()
      .then(res => {
        setRoutes(res.data.routes || []);
        setShowRoutes(true);
        setRouteLoading(false);
      })
      .catch(() => setRouteLoading(false));
  };

  // Build polyline path for each truck route
  const buildRoutePath = (stops) => {
    const path = [DEPOT];
    stops.forEach(stop => path.push([stop.lat, stop.lon]));
    path.push(DEPOT);
    return path;
  };

  if (loading) return (
    <div style={{ textAlign: "center", padding: "60px", fontSize: "18px" }}>
      ⏳ Loading map...
    </div>
  );

  return (
    <div>
      <h2 style={{ marginTop: 0, color: "#1a5276" }}>🗺️ Live Bin Map — Buea</h2>

      {/* CONTROLS */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "16px", flexWrap: "wrap", alignItems: "center" }}>
        <button
          onClick={handleLoadRoutes}
          disabled={routeLoading}
          style={{
            background: routeLoading ? "#aaa" : "linear-gradient(135deg, #1a5276, #2e86c1)",
            color: "white", border: "none", padding: "10px 24px",
            borderRadius: "8px", fontSize: "14px",
            cursor: routeLoading ? "not-allowed" : "pointer",
            boxShadow: "0 2px 6px rgba(0,0,0,0.2)"
          }}
        >
          {routeLoading ? "⏳ Optimizing..." : "🧬 Show Optimized Routes"}
        </button>

        {showRoutes && (
          <button
            onClick={() => { setShowRoutes(false); setRoutes([]); }}
            style={{
              background: "white", color: "#e74c3c",
              border: "2px solid #e74c3c", padding: "10px 24px",
              borderRadius: "8px", fontSize: "14px", cursor: "pointer"
            }}
          >
            ✖ Hide Routes
          </button>
        )}
      </div>

      {/* LEGEND */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "16px", flexWrap: "wrap" }}>
        {[
          ["🟢 Below 60%",  "#2ecc71"],
          ["🟡 60–80%",     "#f39c12"],
          ["🔴 Above 80%",  "#e74c3c"],
          ["📱 Reported",   "#9b59b6"],
        ].map(([label, color]) => (
          <div key={label} style={{
            display: "flex", alignItems: "center", gap: "8px",
            background: "white", padding: "6px 14px",
            borderRadius: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
            fontSize: "13px"
          }}>
            <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: color }} />
            {label}
          </div>
        ))}
        {showRoutes && COLORS.slice(0, routes.length).map((color, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: "8px",
            background: "white", padding: "6px 14px",
            borderRadius: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
            fontSize: "13px"
          }}>
            <div style={{ width: "24px", height: "4px", background: color, borderRadius: "2px" }} />
            TRUCK{i + 1}
          </div>
        ))}
      </div>

      {/* MAP */}
      <div style={{ borderRadius: "12px", overflow: "hidden", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
        <MapContainer
          center={[4.1534, 9.2916]}
          zoom={14}
          style={{ height: "560px", width: "100%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="© OpenStreetMap contributors"
          />

          {/* DEPOT MARKER */}
          <Marker position={DEPOT}>
            <Popup>
              <strong>🏭 HYSACAM Depot</strong><br />
              Buea Collection Base
            </Popup>
          </Marker>

          {/* BIN MARKERS */}
          {predictions.map((bin, i) => (
            <CircleMarker
              key={i}
              center={[bin.lat, bin.lon]}
              radius={bin.needs_collection ? 13 : 9}
              fillColor={bin.community_reported ? "#9b59b6" : getBinColor(bin.predicted_fill)}
              color="white"
              weight={2}
              fillOpacity={0.9}
            >
              <Popup>
                <div style={{ minWidth: "190px" }}>
                  <strong style={{ fontSize: "15px" }}>{bin.name}</strong><br />
                  <span style={{ color: "#666" }}>{bin.neighborhood}</span>
                  <hr style={{ margin: "8px 0" }} />
                  <div>Fill Level:
                    <strong style={{ color: getBinColor(bin.predicted_fill), marginLeft: "6px" }}>
                      {bin.predicted_fill}%
                    </strong>
                  </div>
                  <div>Capacity: {bin.capacity_kg} kg</div>
                  <div>{bin.is_market_area ? "🏪 Market Area" : "🏘️ Residential"}</div>
                  <hr style={{ margin: "8px 0" }} />
                  {bin.community_reported && (
                    <span style={{ color: "#9b59b6", fontWeight: "bold", display: "block" }}>📱 Community Reported</span>
                  )}
                  {bin.needs_collection
                    ? <span style={{ color: "#e74c3c", fontWeight: "bold" }}>⚠️ Needs Collection</span>
                    : <span style={{ color: "#2ecc71" }}>✅ Level OK</span>
                  }
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* ROUTE POLYLINES */}
          {showRoutes && routes.map((route, i) => (
            <Polyline
              key={i}
              positions={buildRoutePath(route.stops)}
              pathOptions={{
                color    : COLORS[i % COLORS.length],
                weight   : 4,
                opacity  : 0.8,
                dashArray: "8 4"
              }}
            />
          ))}

          {/* ROUTE STOP MARKERS */}
          {showRoutes && routes.map((route, i) =>
            route.stops.map((stop, j) => (
              <CircleMarker
                key={`${i}-${j}`}
                center={[stop.lat, stop.lon]}
                radius={8}
                fillColor={COLORS[i % COLORS.length]}
                color="white"
                weight={2}
                fillOpacity={1}
              >
                <Popup>
                  <div style={{ minWidth: "160px" }}>
                    <strong>{stop.name}</strong><br />
                    <span style={{ color: "#666" }}>{stop.neighborhood}</span>
                    <hr style={{ margin: "6px 0" }} />
                    <div>🚛 {route.truck_id} — Stop {stop.stop_order}</div>
                    <div>📦 Demand: {stop.demand_kg} kg</div>
                    <div>Fill: {stop.fill_percentage}%</div>
                  </div>
                </Popup>
              </CircleMarker>
            ))
          )}
        </MapContainer>
      </div>

      {/* ROUTE SUMMARY TABLE */}
      {showRoutes && routes.length > 0 && (
        <div style={{
          background: "white", borderRadius: "12px", padding: "20px",
          marginTop: "20px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
        }}>
          <h3 style={{ marginTop: 0, color: "#1a5276" }}>🚛 Route Summary</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
            <thead>
              <tr style={{ background: "#eaf4fb" }}>
                {["Truck", "Bins", "Load (kg)", "Distance (km)", "Color"].map(h => (
                  <th key={h} style={{ padding: "10px", textAlign: "left", borderBottom: "2px solid #ddd" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {routes.map((route, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "10px", fontWeight: "bold" }}>{route.truck_id}</td>
                  <td style={{ padding: "10px" }}>{route.total_bins}</td>
                  <td style={{ padding: "10px" }}>{route.total_load_kg}</td>
                  <td style={{ padding: "10px" }}>{route.distance_km} km</td>
                  <td style={{ padding: "10px" }}>
                    <div style={{
                      width: "40px", height: "8px",
                      background: COLORS[i % COLORS.length],
                      borderRadius: "4px"
                    }} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}