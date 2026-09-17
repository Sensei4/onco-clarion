import { apiRequest } from "@/lib/api";

import type {
  CancerEvent,
  CancerEventDetail,
  CreateEventPayload,
  EventListParams,
  EventType,
  PaginatedResponse,
} from "./types";

const SUBTYPE_PATHS: Record<EventType, string> = {
  primary_visit: "primary-visits",
  followup_visit: "followup-visits",
  observation_visit: "observation-visits",
  consilium: "consilia",
  hospitalization: "hospitalizations",
  treatment: "treatments",
};

function buildQuery(params: EventListParams): string {
  const query = new URLSearchParams();
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  if (params.case !== undefined) query.set("case", String(params.case));
  if (params.patient !== undefined)
    query.set("patient", String(params.patient));
  if (params.type) query.set("type", params.type);
  if (params.status) query.set("status", params.status);
  if (params.search) query.set("search", params.search);
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchEvents(
  params: EventListParams = {},
): Promise<PaginatedResponse<CancerEvent>> {
  return apiRequest<PaginatedResponse<CancerEvent>>(
    `/events/${buildQuery(params)}`,
  );
}

export async function fetchEvent(id: number): Promise<CancerEventDetail> {
  return apiRequest<CancerEventDetail>(`/events/${id}/`);
}

export async function createEvent(
  type: EventType,
  payload: CreateEventPayload,
): Promise<CancerEventDetail> {
  const path = SUBTYPE_PATHS[type];
  return apiRequest<CancerEventDetail>(`/events/${path}/`, {
    method: "POST",
    body: payload,
  });
}

export async function deleteEvent(type: EventType, id: number): Promise<void> {
  const path = SUBTYPE_PATHS[type];
  await apiRequest<void>(`/events/${path}/${id}/`, { method: "DELETE" });
}
