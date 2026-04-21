import axios from "axios";

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

export async function getProperties(filters = {}) {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== "" && v !== null && v !== undefined)
  );
  const { data } = await API.get("/properties/", { params });
  return data;
}

export async function getMarketSummary(city, operation_type) {
  const { data } = await API.get("/stats/market-summary", {
    params: { city, operation_type },
  });
  return data;
}

export async function getByNeighborhood(city, operation_type) {
  const { data } = await API.get("/stats/by-neighborhood", {
    params: { city, operation_type },
  });
  return data;
}

export async function getPropertyById(id) {
  const { data } = await API.get(`/properties/${id}`);
  return data;
}
