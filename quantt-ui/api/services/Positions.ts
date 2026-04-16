import api from "../axiosInstance.js";

// Make sure you are using await, just for the sake of your mind.

export const getPositions = async (
  page: number,
  pageSize: number,
  symbol?: string,
) => {
  try {
    const response = await api.get("/report/trades", {
      params: {
        page: page,
        page_size: pageSize,
        symbol: symbol,
      },
    });

    return response.data;
  } catch (error) {
    console.error("Error fetching trades:", error);
    throw error;
  }
};
