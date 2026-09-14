const API_BASE = "/api";

/**
 * Read the CSRF token from cookies.
 * Django sets it as a non-HttpOnly cookie named "csrftoken".
 */
function getCsrfToken(): string | null {
  const match = document.cookie.match(/(^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[2]) : null;
}

export interface ApiError {
  status: number;
  detail: string;
  data?: unknown;
}

export class ApiRequestError extends Error {
  status: number;
  data?: unknown;

  constructor({ status, detail, data }: ApiError) {
    super(detail);
    this.name = "ApiRequestError";
    this.status = status;
    this.data = data;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
}

/**
 * Universal fetch wrapper:
 * - prefixes /api
 * - sends cookies (credentials: "include")
 * - adds JSON headers and CSRF token for unsafe methods
 * - parses JSON response
 * - throws ApiRequestError on non-2xx
 */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, headers, method = "GET", ...rest } = options;

  const finalHeaders: Record<string, string> = {
    Accept: "application/json",
    ...(headers as Record<string, string> | undefined),
  };

  const upperMethod = method.toUpperCase();
  const isUnsafe = ["POST", "PUT", "PATCH", "DELETE"].includes(upperMethod);

  if (body !== undefined) {
    finalHeaders["Content-Type"] = "application/json";
  }

  if (isUnsafe) {
    const csrf = getCsrfToken();
    if (csrf) {
      finalHeaders["X-CSRFToken"] = csrf;
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    method: upperMethod,
    credentials: "include",
    headers: finalHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    let detail = `Request failed: ${response.status}`;
    let data: unknown = payload;

    if (isJson && typeof payload === "object" && payload !== null) {
      const obj = payload as Record<string, unknown>;
      if (typeof obj.detail === "string") {
        detail = obj.detail;
      } else {
        detail = JSON.stringify(obj);
      }
      data = obj;
    } else if (typeof payload === "string") {
      detail = payload;
    }

    throw new ApiRequestError({
      status: response.status,
      detail,
      data,
    });
  }

  return payload as T;
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------
export interface HealthResponse {
  status: string;
  service: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health/");
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: "doctor" | "admin";
  organization: number | null;
  organization_name: string | null;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export async function login(payload: LoginPayload): Promise<User> {
  return apiRequest<User>("/auth/login/", {
    method: "POST",
    body: payload,
  });
}

export async function logout(): Promise<void> {
  await apiRequest<void>("/auth/logout/", { method: "POST" });
}

export async function fetchMe(): Promise<User> {
  return apiRequest<User>("/auth/me/");
}
