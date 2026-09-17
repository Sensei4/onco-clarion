export type EventType =
  | "primary_visit"
  | "followup_visit"
  | "observation_visit"
  | "consilium"
  | "hospitalization"
  | "treatment";

export type EventStatus = "planned" | "done" | "cancelled";

export type TreatmentModality =
  | "chemo"
  | "radiation"
  | "surgery"
  | "targeted"
  | "immunotherapy"
  | "other";

export interface CancerEvent {
  id: number;
  type: EventType;
  status: EventStatus;
  case: number;
  case_diagnosis: string;
  patient: number;
  patient_name: string;
  patient_mrn: string;
  organization: number;
  scheduled_at: string;
  occurred_at: string | null;
  author: number;
  author_name: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface PrimaryVisitDetails {
  chief_complaint: string;
  physical_exam: string;
}

export interface FollowupVisitDetails {
  findings: string;
  plan: string;
}

export interface ObservationVisitDetails {
  findings: string;
}

export interface ConsiliumDetails {
  participants: number[];
  participant_names: string[];
  decision: string;
  recommended_plan: string;
}

export interface HospitalizationDetails {
  ward: string;
  reason: string;
  discharge_date: string | null;
}

export interface TreatmentDetails {
  modality: TreatmentModality;
  regimen: string;
  cycle_number: number | null;
  cycle_total: number | null;
  drugs: string;
}

export type EventDetails =
  | PrimaryVisitDetails
  | FollowupVisitDetails
  | ObservationVisitDetails
  | ConsiliumDetails
  | HospitalizationDetails
  | TreatmentDetails;

export interface CancerEventDetail extends CancerEvent {
  details: EventDetails | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface EventListParams {
  page?: number;
  page_size?: number;
  case?: number;
  patient?: number;
  type?: EventType;
  status?: EventStatus;
  search?: string;
}

export interface CreateEventPayload {
  case: number;
  patient: number;
  organization: number;
  status?: EventStatus;
  scheduled_at: string;
  occurred_at?: string | null;
  notes?: string;
  // Subtype-specific fields are added per type
  [key: string]: unknown;
}
