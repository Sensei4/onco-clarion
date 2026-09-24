import { useQuery } from "@tanstack/react-query";

import { fetchIcd11Chapters, fetchIcd11Entity, searchIcd11 } from "./api";
import type { SearchParams } from "./types";

export function useIcd11Search(params: SearchParams, enabled: boolean = true) {
  return useQuery({
    queryKey: ["icd11", "search", params],
    queryFn: () => searchIcd11(params),
    enabled: enabled && params.q.trim().length >= 2,
    staleTime: 60_000, // 1 min — данные ICD-11 не меняются часто
  });
}

export function useIcd11Chapters() {
  return useQuery({
    queryKey: ["icd11", "chapters"],
    queryFn: fetchIcd11Chapters,
    staleTime: 5 * 60_000, // 5 min
  });
}

export function useIcd11Entity(uriSuffix: string | undefined) {
  return useQuery({
    queryKey: ["icd11", "entity", uriSuffix],
    queryFn: () => fetchIcd11Entity(uriSuffix!),
    enabled: !!uriSuffix,
    staleTime: 5 * 60_000,
  });
}
