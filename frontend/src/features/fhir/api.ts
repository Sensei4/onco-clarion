import { apiRequest } from "@/lib/api";

import type { FhirBundle, FhirResource } from "./types";

export async function fetchPatientFhir(
  patientId: number,
): Promise<FhirResource> {
  return apiRequest<FhirResource>(`/fhir/Patient/${patientId}/`);
}

export async function fetchPatientEverything(
  patientId: number,
): Promise<FhirBundle> {
  return apiRequest<FhirBundle>(`/fhir/Patient/${patientId}/$everything/`);
}

/**
 * Trigger a file download in the browser.
 * Uses Blob + temporary <a> element.
 */
export function downloadJson(data: unknown, filename: string): void {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: "application/fhir+json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
