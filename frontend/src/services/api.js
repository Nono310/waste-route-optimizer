import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

export const getBins = () => API.get("/bins");
export const getPredictions = () => API.get("/predict");
export const getOptimizedRoutes = () => API.get("/optimize");
export const submitReport = (data) => API.post("/report", data);
export const getReports = () => API.get("/reports");