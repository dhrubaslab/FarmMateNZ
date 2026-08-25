import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

// Attach the JWT to every request, if we have one
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("farmmate_token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If a request comes back 401 (expired/invalid token), clear session and
// send the user back to login.
api.interceptors.response.use(
  (response) => {
    // Dashboard.vue expects an array from its legacy GET /farms call. The
    // documented endpoint returns one Farm object, so wrap that real response.
    if (response.config.__dashboardSingleFarm && response.data) {
      response.data = [response.data];
    }
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("farmmate_token");
      localStorage.removeItem("farmmate_user");
      localStorage.removeItem("farmmate_me");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;

