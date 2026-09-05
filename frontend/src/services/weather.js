import api from "./api";

export const getWeather = (farmId) => api.get(`/weather/${farmId}`);
export const syncWeather = (farmId) => api.post(`/weather/${farmId}/sync`);