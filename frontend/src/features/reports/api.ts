import { apiRequest } from "@/lib/api";

import type {
  CasesByStageResponse,
  CasesByStatusResponse,
  EventsByTypeResponse,
  ReportDateParams,
  TopDiagnosesResponse,
  WaitingTimeResponse,
} from "./types";

function buildQuery(params: ReportDateParams): string {
  const query = new URLSearchParams();
  if (params.date_from) query.set("date_from", params.date_from);
  if (params.date_to) query.set("date_to", params.date_to);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchCasesByStatus(
  params: ReportDateParams = {},
): Promise<CasesByStatusResponse> {
  return apiRequest<CasesByStatusResponse>(
    `/reports/cases-by-status/${buildQuery(params)}`,
  );
}

export async function fetchCasesByStage(
  params: ReportDateParams = {},
): Promise<CasesByStageResponse> {
  return apiRequest<CasesByStageResponse>(
    `/reports/cases-by-stage/${buildQuery(params)}`,
  );
}

export async function fetchWaitingTime(): Promise<WaitingTimeResponse> {
  return apiRequest<WaitingTimeResponse>("/reports/waiting-time/");
}

export async function fetchEventsByType(
  params: ReportDateParams = {},
): Promise<EventsByTypeResponse> {
  return apiRequest<EventsByTypeResponse>(
    `/reports/events-by-type/${buildQuery(params)}`,
  );
}

export async function fetchTopDiagnoses(
  params: ReportDateParams = {},
): Promise<TopDiagnosesResponse> {
  return apiRequest<TopDiagnosesResponse>(
    `/reports/top-diagnoses/${buildQuery(params)}`,
  );
}
