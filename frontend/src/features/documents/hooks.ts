import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import {
  deleteDocument,
  fetchDocument,
  fetchDocuments,
  updateDocument,
  uploadDocument,
} from "./api";
import type {
  CaseDocument,
  DocumentListParams,
  PaginatedResponse,
  UpdateDocumentPayload,
  UploadDocumentPayload,
} from "./types";

const documentsKey = {
  all: ["documents"] as const,
  list: (params: DocumentListParams) => ["documents", "list", params] as const,
  detail: (id: number) => ["documents", "detail", id] as const,
};

export function useDocuments(
  params: DocumentListParams = {},
  options?: Omit<
    UseQueryOptions<PaginatedResponse<CaseDocument>>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery({
    queryKey: documentsKey.list(params),
    queryFn: () => fetchDocuments(params),
    ...options,
  });
}

export function useDocument(id: number | undefined) {
  return useQuery({
    queryKey: documentsKey.detail(id ?? 0),
    queryFn: () => fetchDocument(id!),
    enabled: id !== undefined && id > 0,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UploadDocumentPayload) => uploadDocument(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsKey.all });
    },
  });
}

export function useUpdateDocument(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateDocumentPayload) => updateDocument(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsKey.all });
      queryClient.invalidateQueries({ queryKey: documentsKey.detail(id) });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentsKey.all });
    },
  });
}
