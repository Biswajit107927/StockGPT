// Single source of truth for backend communication.
// Every component reads through this module. No fetch() calls anywhere else.

import axios from "axios";
import type {
  UniverseResponse,
  SectorsResponse,
} from "../types/universe";

// Base URL for the FastAPI backend. In dev, the backend runs on :8000.
// In production we'll override this via VITE_API_BASE_URL environment variable.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Universe endpoints
export async function listSectors(): Promise<SectorsResponse> {
  const response = await apiClient.get<SectorsResponse>("/universe/sectors");
  return response.data;
}

export async function listUniverse(params?: {
  sector?: string;
  limit?: number;
  min_market_cap?: number;
}): Promise<UniverseResponse> {
  const response = await apiClient.get<UniverseResponse>("/universe", { params });
  return response.data;
}

// Health check (we'll display this somewhere in the UI later)
export interface HealthResponse {
  status: string;
  database: string;
  universe_size?: number;
  timestamp: string;
  version: string;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
}
