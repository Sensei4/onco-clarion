export type DocumentType =
  | "conclusion"
  | "scan"
  | "analysis"
  | "histology"
  | "other";

export interface CaseDocument {
  id: number;
  case: number;
  case_diagnosis: string;
  patient_name: string;
  patient_mrn: string;
  event: number | null;
  referral: number | null;
  organization: number;
  type: DocumentType;
  title: string;
  original_filename: string;
  content_type: string;
  file_size: number | null;
  file_url: string | null;
  uploaded_by: number;
  uploaded_by_name: string;
  uploaded_at: string;
}

export interface CaseDocumentDetail extends CaseDocument {
  file: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DocumentListParams {
  page?: number;
  page_size?: number;
  case?: number;
  event?: number;
  referral?: number;
  type?: DocumentType;
  search?: string;
}

export interface UploadDocumentPayload {
  case: number;
  organization: number;
  type: DocumentType;
  title?: string;
  event?: number | null;
  referral?: number | null;
  file: File;
}

export interface UpdateDocumentPayload {
  type?: DocumentType;
  title?: string;
  event?: number | null;
  referral?: number | null;
}
