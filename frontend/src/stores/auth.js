import { defineStore } from "pinia";
import api from "../services/api";

function readUser() {
  try {
    return JSON.parse(localStorage.getItem("farmmate_user") || "null");
  } catch {
    return null;
  }
}
export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("farmmate_token") || null,
    user: readUser(),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.user?.role || null,
  },


  actions: {
    async login(email, password) {
      // FastAPI's OAuth2PasswordRequestForm expects x-www-form-urlencoded,
      // with the email placed in the "username" field.
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);

      const response = await api.post("/auth/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const { access_token, token_type, role, farm_id, user_id } = response.data;
      if (!access_token) {
        throw new Error("Login succeeded but no access token was returned.");
      }

      this.token = access_token;
      this.user = {
        role,
        farm_id: farm_id ?? null,
        user_id,
        email,
        token_type: token_type || "bearer",
      };

      localStorage.setItem("farmmate_token", access_token);
      localStorage.setItem("farmmate_user", JSON.stringify(this.user));

      return response.data;
    },

    async refreshMe() {
      const response = await api.get("/auth/me");
      localStorage.setItem("farmmate_me", JSON.stringify(response.data));
      return response.data;
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("farmmate_token");
      localStorage.removeItem("farmmate_user");
      localStorage.removeItem("farmmate_me");
    },
  },
});
