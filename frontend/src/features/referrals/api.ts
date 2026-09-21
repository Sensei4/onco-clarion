import { apiRequest } from "@/lib/api";

import type {
  CancelReferralPayload,
  CompleteReferralPayload,
  CreateReferralPayload,
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
