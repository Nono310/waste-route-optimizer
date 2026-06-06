import axios from "axios";

const API = axios.create({
  baseURL: "https://waste-route-optimizer-api.onrender.com/api",
});

export const getBins = () => API.get("/bins");
export const getPredictions = () => API.get("/predict");
export const getOptimizedRoutes = () => API.get("/optimize");
export const submitReport = (data) => API.post("/report", data);
export const getReports = () => API.get("/reports");