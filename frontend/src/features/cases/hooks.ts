import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import {
  createCase,
  fetchCase,
  fetchCases,
  fetchTransitions,
  transitionCase,
  updateCase,
} from "./api";

import type {
  CancerCase,
  CaseListParams,
  CreateCasePayload,
  PaginatedResponse,
  TransitionPayload,
  UpdateCasePayload,
} from "./types";

const casesKey = {
  all: ["cases"] as const,
  list: (params: CaseListParams) => ["cases", "list", params] as const,
  detail: (id: number) => ["cases", "detail", id] as const,
  transitions: (id: number) => ["cases", "transitions", id] as const,
};

export function useCases(
  params: CaseListParams = {},
  options?: Omit<
    UseQueryOptions<PaginatedResponse<CancerCase>>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery({
    queryKey: casesKey.list(params),
    queryFn: () => fetchCases(params),
    ...options,
  });
}

export function useCase(id: number | undefined) {
  return useQuery({
    queryKey: casesKey.detail(id ?? 0),
    queryFn: () => fetchCase(id!),
    enabled: id !== undefined && id > 0,
  });
}

export function useTransitions(caseId: number | undefined) {
  return useQuery({
    queryKey: casesKey.transitions(caseId ?? 0),
    queryFn: () => fetchTransitions(caseId!),
    enabled: caseId !== undefined && caseId > 0,
  });
}

export function useCreateCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateCasePayload) => createCase(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: casesKey.all });
    },
  });
}

export function useUpdateCase(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateCasePayload) => updateCase(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: casesKey.all });
      queryClient.invalidateQueries({ queryKey: casesKey.detail(id) });
    },
  });
}

export function useTransitionCase(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TransitionPayload) => transitionCase(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: casesKey.detail(id) });
      queryClient.invalidateQueries({ queryKey: casesKey.transitions(id) });
      // Also refresh lists (status changed)
      queryClient.invalidateQueries({ queryKey: casesKey.all });
    },
  });
}
