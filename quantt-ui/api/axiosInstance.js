import axios from "axios";

// Create the instance
const api = axios.create({
  // Use an environment variable for the base URL
  baseURL: "http://localhost:8000",
  timeout: 0, // 1.5 seconds
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Request Interceptor
// Useful for attaching Auth tokens to every request automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response Interceptor
// Useful for global error handling (e.g., redirecting on 401 Unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle logout or token refresh logic here
      console.error("Unauthorized! Redirecting...");
    }
    return Promise.reject(error);
  },
);

export default api;
