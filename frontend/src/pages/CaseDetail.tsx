import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Pencil } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { CaseEditDialog } from "@/features/cases/components/CaseEditDialog";
import { CaseTimeline } from "@/features/cases/components/CaseTimeline";
import { CaseTransitionButtons } from "@/features/cases/components/CaseTransitionButtons";
import { useCase, useTransitions } from "@/features/cases/hooks";
import type { CaseStatus } from "@/features/cases/types";
import { DocumentsSection } from "@/features/documents/components/DocumentsSection";
import { EventsSection } from "@/features/events/components/EventsSection";
import { ReferralsSection } from "@/features/referrals/components/ReferralsSection";

const STATUS_VARIANTS: Record<
  CaseStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  new: "outline",
  diagnostic: "secondary",
  consilium: "secondary",
  waiting_hospitalization: "default",
  in_treatment: "default",
  observation: "default",
  remission: "default",
  relapse: "destructive",
  terminal: "destructive",
};

const STATUS_LABELS: Record<CaseStatus, string> = {
  new: "New",
  diagnostic: "Diagnostic",
  consilium: "Consilium",
  waiting_hospitalization: "Waiting for hospitalization",
  in_treatment: "In treatment",
  observation: "Observation",
  remission: "Remission",
  relapse: "Relapse",
  terminal: "Terminal",
};

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function extractIcd11Id(uri: string): string {
  // Extract numeric id from something like:
  // http://id.who.int/icd/release/11/2026-01/mms/1047754165/unspecified
  const match = uri.match(/\/mms\/(\d+)/);
  return match ? match[1] : "";
}

export function CaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const caseId = id ? Number(id) : undefined;
  const [editOpen, setEditOpen] = useState(false);

  const { data: caseData, isLoading, isError, error } = useCase(caseId);
  const { data: transitions, isLoading: transitionsLoading } =
    useTransitions(caseId);

  if (isLoading) {
    return <div className="text-muted-foreground">Loading case…</div>;
  }

  if (isError || !caseData) {
    return (
      <div className="space-y-4">
        <div className="text-destructive">
          Error: {error instanceof Error ? error.message : "Case not found"}
        </div>
        <Button variant="outline" onClick={() => navigate("/patients")}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to patients
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <Link
            to={`/patients/${caseData.patient}`}
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="mr-1 h-3 w-3" />
            Back to patient
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">
            {caseData.diagnosis_code || `Case #${caseData.id}`}
          </h1>
          <p className="text-muted-foreground text-sm">
            {caseData.patient_name}{" "}
            <span className="font-mono text-xs">({caseData.patient_mrn})</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={STATUS_VARIANTS[caseData.status]}>
            {STATUS_LABELS[caseData.status]}
          </Badge>
          <Button variant="outline" onClick={() => setEditOpen(true)}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Available actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CaseTransitionButtons
            caseId={caseData.id}
            currentStatus={caseData.status}
          />
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Diagnosis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Code</span>
              <span className="font-mono">
                {caseData.diagnosis_code || "—"}
              </span>
            </div>
            <Separator />
            <div className="flex flex-col gap-1">
              <span className="text-muted-foreground">Description</span>
              <span className="text-right">
                {caseData.diagnosis_text || "—"}
              </span>
            </div>
            {caseData.icd11_mms_uri && (
              <>
                <Separator />
                <div className="flex justify-between gap-4 items-center">
                  <span className="text-muted-foreground">ICD-11</span>
                  <a
                    href={`https://icd.who.int/browse/2026-01/mms/en#${extractIcd11Id(caseData.icd11_mms_uri)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-muted-foreground hover:underline font-mono truncate max-w-[220px]"
                    title={caseData.icd11_mms_uri}
                  >
                    {caseData.icd11_mms_uri.split("/").slice(-2).join("/")}
                  </a>
                </div>
              </>
            )}
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Verification date</span>
              <span>{formatDate(caseData.verification_date)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Staging
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">T</span>
              <span className="font-mono">{caseData.tnm_t || "—"}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">N</span>
              <span className="font-mono">{caseData.tnm_n || "—"}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">M</span>
              <span className="font-mono">{caseData.tnm_m || "—"}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Stage</span>
              <span className="font-medium">{caseData.stage || "—"}</span>
            </div>
          </CardContent>
        </Card>

        <div className="md:col-span-2">
          <EventsSection
            caseId={caseData.id}
            patientId={caseData.patient}
            organizationId={caseData.organization}
          />
        </div>

        <div className="md:col-span-2">
          <DocumentsSection
            caseId={caseData.id}
            organizationId={caseData.organization}
          />
        </div>

        <div className="md:col-span-2">
          <ReferralsSection
            caseId={caseData.id}
            organizationId={caseData.organization}
          />
        </div>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Status timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            {transitionsLoading ? (
              <p className="text-muted-foreground text-sm">Loading timeline…</p>
            ) : (
              <CaseTimeline transitions={transitions ?? []} />
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Record
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Organization</span>
              <span>{caseData.organization_name}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span>{formatDateTime(caseData.created_at)}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Updated</span>
              <span>{formatDateTime(caseData.updated_at)}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <CaseEditDialog
        caseData={caseData}
        open={editOpen}
        onOpenChange={setEditOpen}
      />
    </div>
  );
}
