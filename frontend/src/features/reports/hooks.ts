import { useQuery } from "@tanstack/react-query";

import {
  fetchCasesByStage,
  fetchCasesByStatus,
  fetchEventsByType,
  fetchTopDiagnoses,
  fetchWaitingTime,
} from "./api";
import type { ReportDateParams } from "./types";

export function useCasesByStatus(params: ReportDateParams = {}) {
  return useQuery({
    queryKey: ["reports", "cases-by-status", params],
    queryFn: () => fetchCasesByStatus(params),
  });
}

export function useCasesByStage(params: ReportDateParams = {}) {
  return useQuery({
    queryKey: ["reports", "cases-by-stage", params],
    queryFn: () => fetchCasesByStage(params),
  });
}

export function useWaitingTime() {
  return useQuery({
    queryKey: ["reports", "waiting-time"],
    queryFn: fetchWaitingTime,
  });
}

export function useEventsByType(params: ReportDateParams = {}) {
  return useQuery({
    queryKey: ["reports", "events-by-type", params],
    queryFn: () => fetchEventsByType(params),
  });
}

export function useTopDiagnoses(params: ReportDateParams = {}) {
  return useQuery({
    queryKey: ["reports", "top-diagnoses", params],
    queryFn: () => fetchTopDiagnoses(params),
  });
}
