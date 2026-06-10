import axios from "axios";

const API = axios.create({
  baseURL: "https://waste-route-optimizer-api.onrender.com/api",
});

export const getBins = () => API.get("/bins");
export const getPredictions = () => API.get("/predict?hour=18&day=5");
export const getOptimizedRoutes = (hour = 18, day = 5) => API.get(`/optimize?hour=${hour}&day=${day}`);
export const submitReport = (data) => API.post("/report", data);
export const getReports = () => API.get("/reports");