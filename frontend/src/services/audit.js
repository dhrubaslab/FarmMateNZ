import api from "./api";

export const getAuditLogs = (limit = 50) => api.get("/audit-logs", { params: { limit } });
