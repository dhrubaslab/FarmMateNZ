import api from "./api";

export async function getMe() {
  return api.get("/auth/me");
}
export async function inviteUser(data) {
  return api.post("/auth/invite", data);
}
export async function resetPassword(data) {
  return api.post("/auth/reset-password", data);
}
