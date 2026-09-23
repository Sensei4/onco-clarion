import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

import { fetchAuditEvents } from "./api";
import type { AuditEvent, AuditListParams, PaginatedResponse } from "./types";

const auditKey = {
  all: ["audit"] as const,
  list: (params: AuditListParams) => ["audit", "list", params] as const,
};

export function useAuditEvents(
  params: AuditListParams = {},
  options?: Omit<
    UseQueryOptions<PaginatedResponse<AuditEvent>>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery({
    queryKey: auditKey.list(params),
    queryFn: () => fetchAuditEvents(params),
    ...options,
  });
}
