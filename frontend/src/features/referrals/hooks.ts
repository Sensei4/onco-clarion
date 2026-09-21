import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import {
  cancelReferral,
  completeReferral,
  createReferral,
  fetchReferral,
  fetchReferrals,
  reopenReferral,
  updateReferral,
} from "./api";
import type {
  CancelReferralPayload,
  CompleteReferralPayload,
  CreateReferralPayload,
  PaginatedResponse,
  Referral,
  ReferralListParams,
  UpdateReferralPayload,
} from "./types";

const referralsKey = {
  all: ["referrals"] as const,
  list: (params: ReferralListParams) => ["referrals", "list", params] as const,
  detail: (id: number) => ["referrals", "detail", id] as const,
};

export function useReferrals(
  params: ReferralListParams = {},
  options?: Omit<
    UseQueryOptions<PaginatedResponse<Referral>>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery({
    queryKey: referralsKey.list(params),
    queryFn: () => fetchReferrals(params),
    ...options,
  });
}

export function useReferral(id: number | undefined) {
  return useQuery({
    queryKey: referralsKey.detail(id ?? 0),
    queryFn: () => fetchReferral(id!),
    enabled: id !== undefined && id > 0,
  });
}

export function useCreateReferral() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateReferralPayload) => createReferral(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: referralsKey.all });
    },
  });
}

export function useUpdateReferral(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateReferralPayload) => updateReferral(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: referralsKey.all });
      queryClient.invalidateQueries({ queryKey: referralsKey.detail(id) });
    },
  });
}

export function useCompleteReferral(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CompleteReferralPayload) =>
      completeReferral(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: referralsKey.all });
      queryClient.invalidateQueries({ queryKey: referralsKey.detail(id) });
    },
  });
}

export function useCancelReferral(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CancelReferralPayload) => cancelReferral(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: referralsKey.all });
      queryClient.invalidateQueries({ queryKey: referralsKey.detail(id) });
    },
  });
}

export function useReopenReferral(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => reopenReferral(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: referralsKey.all });
      queryClient.invalidateQueries({ queryKey: referralsKey.detail(id) });
    },
  });
}
