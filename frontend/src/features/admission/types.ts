export interface AdmissionQueueItem {
  // Case
  id: number;
  diagnosis_code: string;
  diagnosis_text: string;
  stage: string;
  tnm_t: string;
  tnm_n: string;
  tnm_m: string;

  // Patient
  patient: number;
  patient_name: string;
  patient_mrn: string;
  patient_birth_date: string;
  patient_age: number | null;
  patient_sex: "male" | "female" | "other" | "unknown";
  patient_insurance_policy_number: string;

  // Queue context
  waiting_since: string | null;
  waiting_days: number | null;

  // Last consilium
  last_consilium_date: string | null;
  last_consilium_decision: string;
  last_consilium_recommended_plan: string;
}
