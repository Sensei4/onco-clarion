import { apiRequest } from "@/lib/api";

import type { AuditEvent, AuditListParams, PaginatedResponse } from "./types";

function buildQuery(params: AuditListParams): string {
  const query = new URLSearchParams();
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  if (params.action) query.set("action", params.action);
  if (params.entity_type) query.set("entity_type", params.entity_type);
  if (params.entity_id !== undefined)
    query.set("entity_id", String(params.entity_id));
  if (params.user !== undefined) query.set("user", String(params.user));
  if (params.date_from) query.set("date_from", params.date_from);
  if (params.date_to) query.set("date_to", params.date_to);
  if (params.search) query.set("search", params.search);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchAuditEvents(
  params: AuditListParams = {},
): Promise<PaginatedResponse<AuditEvent>> {
  return apiRequest<PaginatedResponse<AuditEvent>>(
    `/audit/${buildQuery(params)}`,
  );
}
