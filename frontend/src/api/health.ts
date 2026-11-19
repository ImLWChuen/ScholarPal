import { apiClient } from "./client";

export interface HealthResponse {
  status: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiClient<HealthResponse>("/api/v1/health");
}

export async function checkApiHealth(signal?: AbortSignal): Promise<void> {
  await apiClient<HealthResponse>("/health", { signal });
}
