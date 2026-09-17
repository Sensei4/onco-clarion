import { apiRequest } from "@/lib/api";

import type {
  CancerCase,
  CancerCaseDetail,
  CaseListParams,
  CreateCasePayload,
  PaginatedResponse,
  StatusTransition,
  TransitionPayload,
  UpdateCasePayload,
} from "./types";

function buildQuery(params: CaseListParams): string {
  const query = new URLSearchParams();
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  if (params.patient !== undefined)
    query.set("patient", String(params.patient));
  if (params.status) query.set("status", params.status);
  if (params.search) query.set("search", params.search);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchCases(
  params: CaseListParams = {},
): Promise<PaginatedResponse<CancerCase>> {
  return apiRequest<PaginatedResponse<CancerCase>>(
    `/cases/${buildQuery(params)}`,
  );
}

export async function fetchCase(id: number): Promise<CancerCaseDetail> {
  return apiRequest<CancerCaseDetail>(`/cases/${id}/`);
}

export async function createCase(
  payload: CreateCasePayload,
): Promise<CancerCaseDetail> {
  return apiRequest<CancerCaseDetail>("/cases/", {
    method: "POST",
    body: payload,
  });
}

export async function updateCase(
  id: number,
  payload: UpdateCasePayload,
): Promise<CancerCaseDetail> {
  return apiRequest<CancerCaseDetail>(`/cases/${id}/`, {
    method: "PATCH",
    body: payload,
  });
}

export async function transitionCase(
  id: number,
  payload: TransitionPayload,
): Promise<CancerCaseDetail> {
  return apiRequest<CancerCaseDetail>(`/cases/${id}/transition/`, {
    method: "POST",
    body: payload,
  });
}

export async function fetchTransitions(
  id: number,
): Promise<StatusTransition[]> {
  return apiRequest<StatusTransition[]>(`/cases/${id}/transitions/`);
}

export interface WaitingListCase extends CancerCaseDetail {
  waiting_since: string | null;
  waiting_days: number | null;
}

export async function fetchWaitingList(): Promise<WaitingListCase[]> {
  return apiRequest<WaitingListCase[]>("/cases/waiting-list/");
}
