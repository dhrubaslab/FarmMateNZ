import api from "./api";

// Paddock API contract — note the composite key: paddock_id is only unique
// WITHIN a farm, so every lookup/update/delete needs both farm_id and
// paddock_id, unlike Farms which uses farm_id alone.
export const listPaddocks = () => api.get("/paddocks");

export const createPaddock = (data) =>
  api.post("/paddocks", {
    name: data.name,
    farm_id: data.farm_id,
    area_hectares: Number(data.area_hectares),
    stock_type: data.stock_type || null,
  });

export const getPaddock = (farmId, paddockId) =>
  api.get(`/paddocks/${encodeURIComponent(farmId)}/${encodeURIComponent(paddockId)}`);

export const updatePaddock = (farmId, paddockId, data) =>
  api.patch(`/paddocks/${encodeURIComponent(farmId)}/${encodeURIComponent(paddockId)}`, {
    name: data.name,
    farm_id: data.farm_id,
    area_hectares: Number(data.area_hectares),
    stock_type: data.stock_type || null,
  });

export const deletePaddock = (farmId, paddockId) =>
  api.delete(`/paddocks/${encodeURIComponent(farmId)}/${encodeURIComponent(paddockId)}`);

// Status is a query parameter, matching the Farms status-update contract.
export const setPaddockStatus = (farmId, paddockId, status) =>
  api.patch(
    `/paddocks/${encodeURIComponent(farmId)}/${encodeURIComponent(paddockId)}/status`,
    null,
    { params: { status } }
  );