import { useQuery } from "@tanstack/react-query";

import { fetchAdmissionQueue } from "./api";

export function useAdmissionQueue() {
  return useQuery({
    queryKey: ["admission", "queue"] as const,
    queryFn: fetchAdmissionQueue,
    staleTime: 30_000,
  });
}
