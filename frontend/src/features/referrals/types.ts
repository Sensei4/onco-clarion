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
  search?: string;
}

export interface CreateReferralPayload {
  case: number;
  organization: number;
  type: ReferralType;
  title?: string;
  notes?: string;
  event?: number | null;
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
