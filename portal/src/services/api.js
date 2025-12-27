import axios from "axios";

export const apiBase = import.meta.env.VITE_API_BASE ?? "https://admin-grupo05.proyecto2025.linti.unlp.edu.ar"

const api = axios.create({
    withCredentials: true,
    baseURL: apiBase + "/api",
});

api.interceptors.request.use((config) => {
  const csrf = getCookie("csrf_access_token");
  if (csrf) {
    config.headers["X-CSRF-TOKEN"] = csrf;
  }
  return config;
});

function getCookie(name) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(name + "="))
    ?.split("=")[1];
}

export default api;
