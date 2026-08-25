import api from "./api";

// Farm API contract from the FastAPI documentation.
export const listFarms = () => api.get("/farms");
export const createFarm = (data) =>
  api.post("/farms", {
    name: data.name,
    region: data.region,
    size_hectares: Number(data.size_hectares),
  });

export const getFarm = (farmId) => 
  api.get(`/farms/${encodeURIComponent(farmId)}`);

export const updateFarm = (farmId, data) =>
  api.patch(`/farms/${encodeURIComponent(farmId)}`, {
    name: data.name,
    region: data.region,
    size_hectares: Number(data.size_hectares),
  });
  
export const deleteFarm = (farmId) =>
  api.delete(`/farms/${encodeURIComponent(farmId)}`);


// The Swagger contract defines status as a query parameter, not a JSON body.
export const setFarmStatus = (farmId, status) =>
  api.patch(`/farms/${encodeURIComponent(farmId)}/status`, null, {
    params: { status },
  });
