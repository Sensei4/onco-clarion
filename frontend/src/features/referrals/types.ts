export type ReferralType =
  | "lab"
  | "histology"
  | "cytology"
  | "imaging"
  | "other";

export type ReferralStatus = "ordered" | "completed" | "cancelled";

export interface Referral {
  id: number;
  case: number;
  case_diagnosis: string;
  patient_name: string;
  patient_mrn: string;
  event: number | null;
  organization: number;
  type: ReferralType;
  status: ReferralStatus;
  title: string;
  department: number | null;
  department_name: string | null;
  method: number | null;
  method_name: string | null;
  assigned_to: number | null;
  assigned_to_name: string | null;
  scheduled_at: string | null;
  room: string;
  ordered_by: number;
  ordered_by_name: string;
  ordered_at: string;
  result_received_at: string | null;
}

export interface ReferralDetail extends Referral {
  notes: string;
  result_text: string;
  completed_by: number | null;
  completed_by_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ReferralListParams {
  page?: number;
  page_size?: number;
  case?: number;
  event?: number;
  type?: ReferralType;
  status?: ReferralStatus;
  department?: number;
  method?: number;
  assigned_to?: number;
  scheduled_from?: string;
  scheduled_to?: string;
  search?: string;
}

export interface CreateReferralPayload {
  case: number;
  organization: number;
  type?: ReferralType;
  title?: string;
  notes?: string;
  event?: number | null;
  department?: number | null;
  method?: number | null;
  assigned_to?: number | null;
  scheduled_at?: string | null;
  room?: string;
}

export interface UpdateReferralPayload {
  type?: ReferralType;
  title?: string;
  notes?: string;
  event?: number | null;
}

export interface CompleteReferralPayload {
  result_text?: string;
}

export interface CancelReferralPayload {
  reason?: string;
}

// ---------------------------------------------------------------------------
// Diagnostic departments and methods (Stage 16)
// ---------------------------------------------------------------------------

export type DiagnosticCategory =
  | "laboratory"
  | "pathology"
  | "imaging"
  | "endoscopy"
  | "functional"
  | "surgery"
  | "molecular"
  | "other";

export interface DiagnosticMethod {
  id: number;
  department: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface DiagnosticDepartment {
  id: number;
  name: string;
  category: DiagnosticCategory;
  is_active: boolean;
  methods: DiagnosticMethod[];
}
