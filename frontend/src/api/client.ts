const API_BASE_URL = import.meta.env.VITE_API_URL || "";

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function parseErrorMessage(response: Response): Promise<{ message: string; details: unknown }> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") {
      return { message: body.detail, details: body };
    }
    if (Array.isArray(body?.detail)) {
      const msgs = body.detail
        .map((err: { loc?: unknown[]; msg?: string }) => {
          const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : undefined;
          return field ? `${String(field)}: ${err.msg ?? "Invalid value"}` : err.msg ?? "Invalid value";
        })
        .join("; ");
      return { message: msgs || "Validation failed", details: body.detail };
    }
    if (typeof body?.message === "string") {
      return { message: body.message, details: body };
    }
    return { message: `Request failed (${response.status})`, details: body };
  } catch {
    return { message: `API Error: ${response.status} ${response.statusText}`, details: null };
  }
}

async function tryRefreshToken(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const url = `${API_BASE_URL}/api/v1/auth/refresh`;
      const res = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        setAccessToken(null);
        return null;
      }
      const data = (await res.json()) as { access_token?: string };
      if (data.access_token) {
        setAccessToken(data.access_token);
        return data.access_token;
      }
      setAccessToken(null);
      return null;
    } catch {
      setAccessToken(null);
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit & { skipAuthRefresh?: boolean }
): Promise<T> {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string> | undefined),
  };

  if (accessToken && !headers.Authorization) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, {
    ...options,
    credentials: "include",
    headers,
  });

  const isAuthEndpoint =
    endpoint.includes("/auth/login") ||
    endpoint.includes("/auth/register") ||
    endpoint.includes("/auth/refresh");

  if (response.status === 401 && !isAuthEndpoint && !options?.skipAuthRefresh) {
    const newToken = await tryRefreshToken();
    if (newToken) {
      const retryHeaders = { ...headers, Authorization: `Bearer ${newToken}` };
      const retryResponse = await fetch(url, {
        ...options,
        credentials: "include",
        headers: retryHeaders,
      });
      if (!retryResponse.ok) {
        const { message, details } = await parseErrorMessage(retryResponse);
        throw new ApiError(retryResponse.status, message, details);
      }
      if (retryResponse.status === 204) {
        return undefined as T;
      }
      return retryResponse.json();
    }
  }

  if (!response.ok) {
    const { message, details } = await parseErrorMessage(response);
    throw new ApiError(response.status, message, details);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}
