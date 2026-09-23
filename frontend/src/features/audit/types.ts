export type AuditAction =
  | "view"
  | "create"
  | "update"
  | "delete"
  | "download"
  | "login"
  | "logout";

export interface AuditEvent {
  id: number;
  user: number | null;
  user_name: string | null;
  action: AuditAction;
  entity_type: string;
  entity_id: number | null;
  entity_repr: string;
  organization: number | null;
  organization_name: string | null;
  timestamp: string;
  ip_address: string | null;
  user_agent: string;
  request_method: string;
  request_path: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuditListParams {
  page?: number;
  page_size?: number;
  action?: AuditAction;
  entity_type?: string;
  entity_id?: number;
  user?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
}
