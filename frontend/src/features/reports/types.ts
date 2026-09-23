export interface CountItem {
  count: number;
}

export interface StatusCount extends CountItem {
  status: string;
  label: string;
}

export interface StageCount extends CountItem {
  stage: string;
}

export interface TypeCount extends CountItem {
  type: string;
  label: string;
}

export interface DiagnosisCount extends CountItem {
  diagnosis_code: string;
}

export interface CasesByStatusResponse {
  total: number;
  results: StatusCount[];
}

export interface CasesByStageResponse {
  total: number;
  results: StageCount[];
}

export interface EventsByTypeResponse {
  total: number;
  results: TypeCount[];
}

export interface TopDiagnosesResponse {
  results: DiagnosisCount[];
}

export interface WaitingCase {
  case_id: number;
  patient_name: string;
  patient_mrn: string;
  diagnosis_code: string;
  stage: string;
  waiting_since: string;
  waiting_days: number;
}

export interface WaitingTimeResponse {
  total: number;
  avg_days: number;
  median_days: number;
  max_days: number;
  top: WaitingCase[];
}

export interface ReportDateParams {
  date_from?: string;
  date_to?: string;
}
