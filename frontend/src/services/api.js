import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

// Attach the JWT to every request, if we have one
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("farmmate_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If a request comes back 401 (expired/invalid token), clear session and
// send the user back to login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("farmmate_token");
      localStorage.removeItem("farmmate_user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;