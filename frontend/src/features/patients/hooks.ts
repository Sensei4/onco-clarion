import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import {
  createPatient,
  deletePatient,
  fetchPatient,
  fetchPatients,
  updatePatient,
} from "./api";

import type {
  CreatePatientPayload,
  PaginatedResponse,
  Patient,
  PatientListParams,
  UpdatePatientPayload,
} from "./types";

const patientsKey = {
  all: ["patients"] as const,
  list: (params: PatientListParams) => ["patients", "list", params] as const,
  detail: (id: number) => ["patients", "detail", id] as const,
};

export function usePatients(
  params: PatientListParams = {},
  options?: Omit<
    UseQueryOptions<PaginatedResponse<Patient>>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery({
    queryKey: patientsKey.list(params),
    queryFn: () => fetchPatients(params),
    ...options,
  });
}

export function usePatient(id: number | undefined) {
  return useQuery({
    queryKey: patientsKey.detail(id ?? 0),
    queryFn: () => fetchPatient(id!),
    enabled: id !== undefined && id > 0,
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreatePatientPayload) => createPatient(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: patientsKey.all });
    },
  });
}

export function useUpdatePatient(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdatePatientPayload) => updatePatient(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: patientsKey.all });
      queryClient.invalidateQueries({ queryKey: patientsKey.detail(id) });
    },
  });
}

export function useDeletePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deletePatient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: patientsKey.all });
    },
  });
}
