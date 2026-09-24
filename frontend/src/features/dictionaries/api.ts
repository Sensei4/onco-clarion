import { apiRequest } from "@/lib/api";

import type {
  ChapterCount,
  MmsEntity,
  PaginatedResponse,
  SearchParams,
} from "./types";

function buildQuery(params: SearchParams): string {
  const query = new URLSearchParams();
  query.set("q", params.q);
  if (params.chapter) query.set("chapter", params.chapter);
  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.page_size !== undefined)
    query.set("page_size", String(params.page_size));
  return query.toString();
}

export async function searchIcd11(
  params: SearchParams,
): Promise<PaginatedResponse<MmsEntity>> {
  return apiRequest<PaginatedResponse<MmsEntity>>(
    `/dictionaries/icd11/search/?${buildQuery(params)}`,
  );
}

export async function fetchIcd11Chapters(): Promise<ChapterCount[]> {
  return apiRequest<ChapterCount[]>("/dictionaries/icd11/chapters/");
}

export async function fetchIcd11Entity(uriSuffix: string): Promise<MmsEntity> {
  return apiRequest<MmsEntity>(`/dictionaries/icd11/entities/${uriSuffix}/`);
}
