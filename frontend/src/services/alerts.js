import api from "./api";

export const listAlerts = (farmId) => api.get(`/alerts/${farmId}`);
export const acknowledgeAlert = (farmId, alertType) =>
  api.post(`/alerts/${farmId}/${alertType}/acknowledge`);