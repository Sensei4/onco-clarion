import { apiRequest } from "@/lib/api";

import type {
  CancelReferralPayload,
  CompleteReferralPayload,
  CreateReferralPayload,
  DepartmentsListParams,
  DiagnosticCategory,
  DiagnosticDepartment,
  DiagnosticMethod,
  PaginatedResponse,
  Referral,
  ReferralDetail,
  ReferralListParams,
  UpdateReferralPayload,
} from "./types";

function buildQuery(params: ReferralListParams): string {
  const query = new URLSearchParams();
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  if (params.case !== undefined) query.set("case", String(params.case));
  if (params.event !== undefined) query.set("event", String(params.event));
  if (params.type) query.set("type", params.type);
  if (params.status) query.set("status", params.status);
  if (params.department !== undefined)
    query.set("department", String(params.department));
  if (params.method !== undefined) query.set("method", String(params.method));
  if (params.assigned_to !== undefined)
    query.set("assigned_to", String(params.assigned_to));
  if (params.scheduled_from) query.set("scheduled_from", params.scheduled_from);
  if (params.scheduled_to) query.set("scheduled_to", params.scheduled_to);
  if (params.search) query.set("search", params.search);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchReferrals(
  params: ReferralListParams = {},
): Promise<PaginatedResponse<Referral>> {
  return apiRequest<PaginatedResponse<Referral>>(
    `/referrals/${buildQuery(params)}`,
  );
}

export async function fetchReferral(id: number): Promise<ReferralDetail> {
  return apiRequest<ReferralDetail>(`/referrals/${id}/`);
}

export async function createReferral(
  payload: CreateReferralPayload,
): Promise<ReferralDetail> {
  return apiRequest<ReferralDetail>("/referrals/", {
    method: "POST",
    body: payload,
  });
}

export async function updateReferral(
  id: number,
  payload: UpdateReferralPayload,
): Promise<ReferralDetail> {
  return apiRequest<ReferralDetail>(`/referrals/${id}/`, {
    method: "PATCH",
    body: payload,
  });
}

export async function completeReferral(
  id: number,
  payload: CompleteReferralPayload,
): Promise<ReferralDetail> {
  return apiRequest<ReferralDetail>(`/referrals/${id}/complete/`, {
    method: "POST",
    body: payload,
  });
}

export async function cancelReferral(
  id: number,
  payload: CancelReferralPayload,
): Promise<ReferralDetail> {
  return apiRequest<ReferralDetail>(`/referrals/${id}/cancel/`, {
    method: "POST",
    body: payload,
  });
}

export async function reopenReferral(id: number): Promise<ReferralDetail> {
  return apiRequest<ReferralDetail>(`/referrals/${id}/reopen/`, {
    method: "POST",
  });
}

// ---------------------------------------------------------------------------
// Diagnostic departments and methods (Stage 16)
// ---------------------------------------------------------------------------

export interface DepartmentsListParams {
  category?: DiagnosticCategory;
  is_active?: boolean;
}

export async function fetchDiagnosticDepartments(
  params: DepartmentsListParams = {},
): Promise<PaginatedResponse<DiagnosticDepartment>> {
  const query = new URLSearchParams();
  if (params.category) query.set("category", params.category);
  if (params.is_active !== undefined)
    query.set("is_active", String(params.is_active));
  const qs = query.toString();
  return apiRequest<PaginatedResponse<DiagnosticDepartment>>(
    `/referrals/departments/${qs ? `?${qs}` : ""}`,
  );
}

export async function fetchDiagnosticMethods(
  departmentId?: number,
): Promise<PaginatedResponse<DiagnosticMethod>> {
  const query = new URLSearchParams();
  if (departmentId !== undefined) query.set("department", String(departmentId));
  const qs = query.toString();
  return apiRequest<PaginatedResponse<DiagnosticMethod>>(
    `/referrals/methods/${qs ? `?${qs}` : ""}`,
  );
}
