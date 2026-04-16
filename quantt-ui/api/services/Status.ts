import api from "../axiosInstance.js";

// Make sure you are using await, just for the sake of your mind.

export const getStatus = async () => {
  try {
    const response = await api.get("/bot/status");
    return response.data;
  } catch (error) {
    console.error("Error fetching trades:", error);
    throw error;
  }
};
