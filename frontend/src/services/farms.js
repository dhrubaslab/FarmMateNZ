import api from "./api";

export const createFarm = (data) => api.post("/farms", data);
export const getFarm = (farmId) => api.get(`/farms/${encodeURIComponent(farmId)}`);
export const updateFarm = (farmId, data) =>
  api.patch(`/farms/${encodeURIComponent(farmId)}`, data);
export const deleteFarm = (farmId) =>
  api.delete(`/farms/${encodeURIComponent(farmId)}`);
export const setFarmStatus = (farmId, status) =>
  api.patch(`/farms/${encodeURIComponent(farmId)}/status`, null, {
    params: { status },
  });
