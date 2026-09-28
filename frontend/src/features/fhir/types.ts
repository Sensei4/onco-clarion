export interface FhirResource {
  resourceType: string;
  id?: string;
  [key: string]: unknown;
}

export interface FhirBundleEntry {
  fullUrl: string;
  resource: FhirResource;
}

export interface FhirBundle extends FhirResource {
  resourceType: "Bundle";
  type: string;
  total?: number;
  entry?: FhirBundleEntry[];
}
