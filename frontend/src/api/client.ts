import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL });

// Attach the JWT to every request.
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize the API error envelope and handle expired sessions.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    const envelope = error.response?.data?.error;
    const message =
      envelope?.message || error.message || "Unexpected error";
    return Promise.reject(new Error(message));
  }
);

/** Unwrap the { success, data } envelope. */
export function unwrap<T>(payload: { data: T }): T {
  return payload.data;
}
