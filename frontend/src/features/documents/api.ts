import { apiRequest } from "@/lib/api";

import type {
  CaseDocument,
  CaseDocumentDetail,
  DocumentListParams,
  PaginatedResponse,
  UpdateDocumentPayload,
  UploadDocumentPayload,
} from "./types";

function buildQuery(params: DocumentListParams): string {
  const query = new URLSearchParams();
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  if (params.case !== undefined) query.set("case", String(params.case));
  if (params.event !== undefined) query.set("event", String(params.event));
  if (params.referral !== undefined)
    query.set("referral", String(params.referral));
  if (params.type) query.set("type", params.type);
  if (params.search) query.set("search", params.search);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchDocuments(
  params: DocumentListParams = {},
): Promise<PaginatedResponse<CaseDocument>> {
  return apiRequest<PaginatedResponse<CaseDocument>>(
    `/documents/${buildQuery(params)}`,
  );
}

export async function fetchDocument(id: number): Promise<CaseDocumentDetail> {
  return apiRequest<CaseDocumentDetail>(`/documents/${id}/`);
}

export async function uploadDocument(
  payload: UploadDocumentPayload,
): Promise<CaseDocumentDetail> {
  const formData = new FormData();
  formData.append("case", String(payload.case));
  formData.append("organization", String(payload.organization));
  formData.append("type", payload.type);
  if (payload.title) formData.append("title", payload.title);
  if (payload.event !== undefined && payload.event !== null) {
    formData.append("event", String(payload.event));
  }
  if (payload.referral !== undefined && payload.referral !== null) {
    formData.append("referral", String(payload.referral));
  }
  formData.append("file", payload.file);

  return apiRequest<CaseDocumentDetail>("/documents/", {
    method: "POST",
    body: formData,
  });
}

export async function updateDocument(
  id: number,
  payload: UpdateDocumentPayload,
): Promise<CaseDocumentDetail> {
  return apiRequest<CaseDocumentDetail>(`/documents/${id}/`, {
    method: "PATCH",
    body: payload,
  });
}

export async function deleteDocument(id: number): Promise<void> {
  await apiRequest<void>(`/documents/${id}/`, { method: "DELETE" });
}

export function getDownloadUrl(id: number): string {
  return `/api/documents/${id}/download/`;
}
