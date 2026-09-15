export type PatientSex = "male" | "female" | "other" | "unknown";
export type PatientVitalStatus = "alive" | "dead";

export interface Patient {
  id: number;
  full_name: string;
  medical_record_number: string;
  birth_date: string; // ISO date
  sex: PatientSex;
  vital_status: PatientVitalStatus;
  organization: number;
  organization_name: string;
  created_at: string;
}

export interface PatientDetail extends Patient {
  contacts: Record<string, unknown>;
  age: number | null;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface PatientListParams {
  page?: number;
  page_size?: number;
  search?: string;
}

export interface CreatePatientPayload {
  organization: number;
  full_name: string;
  birth_date: string;
  sex: PatientSex;
  medical_record_number: string;
  contacts?: Record<string, unknown>;
  vital_status?: PatientVitalStatus;
}

export type UpdatePatientPayload = Partial<
  Omit<CreatePatientPayload, "organization">
>;
