import api from "../axiosInstance.js";

// Make sure you are using await, just for the sake of your mind.

export const getSummary = async () => {
  try {
    const response = await api.get("/report/summary");

    return response.data;
  } catch (error) {
    console.error("Error fetching summary:", error);
    throw error;
  }
};
