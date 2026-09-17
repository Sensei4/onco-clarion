import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import { createEvent, deleteEvent, fetchEvent, fetchEvents } from "./api";
import type {
  CancerEvent,
  CreateEventPayload,
  EventListParams,
  EventType,
  PaginatedResponse,
} from "./types";

const eventsKey = {
  all: ["events"] as const,
  list: (params: EventListParams) => ["events", "list", params] as const,
  detail: (id: number) => ["events", "detail", id] as const,
};

export function useEvents(
  params: EventListParams = {},
  options?: Omit<
    UseQueryOptions<PaginatedResponse<CancerEvent>>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery({
    queryKey: eventsKey.list(params),
    queryFn: () => fetchEvents(params),
    ...options,
  });
}

export function useEvent(id: number | undefined) {
  return useQuery({
    queryKey: eventsKey.detail(id ?? 0),
    queryFn: () => fetchEvent(id!),
    enabled: id !== undefined && id > 0,
  });
}

export function useCreateEvent(type: EventType) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateEventPayload) => createEvent(type, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: eventsKey.all });
    },
  });
}

export function useDeleteEvent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ type, id }: { type: EventType; id: number }) =>
      deleteEvent(type, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: eventsKey.all });
    },
  });
}
