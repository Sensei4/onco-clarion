export type CaseStatus =
  | "new"
  | "diagnostic"
  | "consilium"
  | "waiting_hospitalization"
  | "in_treatment"
  | "observation"
  | "remission"
  | "relapse"
  | "terminal";

export interface CancerCase {
  id: number;
  patient: number;
  patient_name: string;
  patient_mrn: string;
  organization: number;
  organization_name: string;
  diagnosis_code: string;
  stage: string;
  status: CaseStatus;
  created_at: string;
}

export interface CancerCaseDetail extends CancerCase {
  diagnosis_text: string;
  verification_date: string | null;
  tnm_t: string;
  tnm_n: string;
  tnm_m: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CaseListParams {
  page?: number;
  page_size?: number;
  patient?: number;
  status?: CaseStatus;
  search?: string;
}

export interface CreateCasePayload {
  patient: number;
  organization: number;
  diagnosis_code?: string;
  diagnosis_text?: string;
  verification_date?: string | null;
  tnm_t?: string;
  tnm_n?: string;
  tnm_m?: string;
  stage?: string;
}

export type UpdateCasePayload = Partial<
  Omit<CreateCasePayload, "patient" | "organization">
>;

export interface StatusTransition {
  id: number;
  from_status: string;
  to_status: string;
  transitioned_by: number | null;
  transitioned_by_name: string | null;
  transitioned_at: string;
  reason: string;
}

export interface TransitionPayload {
  action: string;
  reason?: string;
}
