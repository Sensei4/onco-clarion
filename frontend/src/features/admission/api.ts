import { apiRequest } from "@/lib/api";

import type { AdmissionQueueItem } from "./types";

export async function fetchAdmissionQueue(): Promise<AdmissionQueueItem[]> {
  return apiRequest<AdmissionQueueItem[]>("/cases/admission-queue/");
}
