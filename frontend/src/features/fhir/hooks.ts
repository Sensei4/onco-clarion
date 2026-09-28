import { useMutation } from "@tanstack/react-query";

import { downloadJson, fetchPatientEverything, fetchPatientFhir } from "./api";

export function useExportPatientFhir() {
  return useMutation({
    mutationFn: async (patientId: number) => {
      const data = await fetchPatientFhir(patientId);
      downloadJson(data, `patient-${patientId}-fhir.json`);
    },
  });
}

export function useExportPatientEverything() {
  return useMutation({
    mutationFn: async (patientId: number) => {
      const data = await fetchPatientEverything(patientId);
      downloadJson(data, `patient-${patientId}-everything.json`);
    },
  });
}
