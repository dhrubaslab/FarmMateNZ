import { defineStore } from "pinia";
import api from "../services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("farmmate_token") || null,
    user: JSON.parse(localStorage.getItem("farmmate_user") || "null"),
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

      const { access_token, role, farm_id, user_id } = response.data;

      this.token = access_token;
      this.user = { role, farm_id, user_id, email };

      localStorage.setItem("farmmate_token", access_token);
      localStorage.setItem("farmmate_user", JSON.stringify(this.user));
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("farmmate_token");
      localStorage.removeItem("farmmate_user");
    },
  },
});