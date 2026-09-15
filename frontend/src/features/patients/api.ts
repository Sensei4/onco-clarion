import { apiRequest } from "@/lib/api";

import type {
  CreatePatientPayload,
  PaginatedResponse,
  Patient,
  PatientDetail,
  PatientListParams,
  UpdatePatientPayload,
} from "./types";

function buildQuery(params: PatientListParams): string {
  const query = new URLSearchParams();
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  if (params.search) query.set("search", params.search);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchPatients(
  params: PatientListParams = {},
): Promise<PaginatedResponse<Patient>> {
  return apiRequest<PaginatedResponse<Patient>>(
    `/patients/${buildQuery(params)}`,
  );
}

export async function fetchPatient(id: number): Promise<PatientDetail> {
  return apiRequest<PatientDetail>(`/patients/${id}/`);
}

export async function createPatient(
  payload: CreatePatientPayload,
): Promise<PatientDetail> {
  return apiRequest<PatientDetail>("/patients/", {
    method: "POST",
    body: payload,
  });
}

export async function updatePatient(
  id: number,
  payload: UpdatePatientPayload,
): Promise<PatientDetail> {
  return apiRequest<PatientDetail>(`/patients/${id}/`, {
    method: "PATCH",
    body: payload,
  });
}

export async function deletePatient(id: number): Promise<void> {
  await apiRequest<void>(`/patients/${id}/`, { method: "DELETE" });
}
