import { useState } from "react";
import { ArrowLeft, UserCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAdmissionQueue } from "@/features/admission/hooks";
import type { AdmissionQueueItem } from "@/features/admission/types";
import { CaseTransitionButtons } from "@/features/cases/components/CaseTransitionButtons";
import { cn } from "@/lib/utils";

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const SEX_LABELS: Record<string, string> = {
  male: "Male",
  female: "Female",
  other: "Other",
  unknown: "Unknown",
};

const QUEUE_PREVIEW_LIMIT = 20;

export function Admission() {
  const {
    data: queue,
    isLoading,
    isError,
    error,
    refetch,
  } = useAdmissionQueue();

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [showAll, setShowAll] = useState(false);

  const items = queue ?? [];
  const visibleItems = showAll ? items : items.slice(0, QUEUE_PREVIEW_LIMIT);

  const selectedItem = selectedId
    ? (items.find((i) => i.id === selectedId) ?? null)
    : null;

  // ----------------------------------------------------------------
  // Detail view (single patient)
  // ----------------------------------------------------------------
  if (selectedItem) {
    return (
      <AdmissionDetail
        item={selectedItem}
        onBack={() => {
          setSelectedId(null);
          refetch();
        }}
      />
    );
  }

  // ----------------------------------------------------------------
  // List view
  // ----------------------------------------------------------------
  const nextInQueue = items[0] ?? null;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Admission desk</h1>
          <p className="text-muted-foreground">
            {isLoading
              ? "Loading…"
              : `${items.length} patient${items.length === 1 ? "" : "s"} waiting for admission`}
          </p>
        </div>
        {nextInQueue && (
          <Button onClick={() => setSelectedId(nextInQueue.id)}>
            <UserCheck className="mr-2 h-4 w-4" />
            Call next patient
          </Button>
        )}
      </div>

      {isLoading && <div className="text-muted-foreground">Loading queue…</div>}

      {isError && (
        <div className="text-destructive">
          Error: {error instanceof Error ? error.message : "Unknown error"}
        </div>
      )}

      {!isLoading && items.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            No patients waiting for admission.
          </CardContent>
        </Card>
      )}

      {items.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Waiting list (longest first)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patient</TableHead>
                  <TableHead>MRN</TableHead>
                  <TableHead>Age</TableHead>
                  <TableHead>Diagnosis</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Waiting since</TableHead>
                  <TableHead>Waiting</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visibleItems.map((item, idx) => {
                  const isNext = idx === 0;
                  return (
                    <TableRow
                      key={item.id}
                      className={cn(
                        "cursor-pointer",
                        isNext
                          ? "bg-primary/10 hover:bg-primary/15"
                          : "hover:bg-accent",
                      )}
                      onClick={() => setSelectedId(item.id)}
                    >
                      <TableCell className="font-medium">
                        {item.patient_name}
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {item.patient_mrn}
                      </TableCell>
                      <TableCell className="text-sm">
                        {item.patient_age ?? "—"}
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {item.diagnosis_code || "—"}
                      </TableCell>
                      <TableCell className="text-sm">
                        {item.stage || "—"}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                        {formatDate(item.waiting_since)}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            item.waiting_days != null && item.waiting_days > 7
                              ? "destructive"
                              : "outline"
                          }
                        >
                          {item.waiting_days != null
                            ? `${item.waiting_days} d`
                            : "—"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>

          {!showAll && items.length > QUEUE_PREVIEW_LIMIT && (
            <div className="border-t p-3 text-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAll(true)}
              >
                Show all {items.length} patients
              </Button>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Detail view: one patient card
// ---------------------------------------------------------------------------

interface AdmissionDetailProps {
  item: AdmissionQueueItem;
  onBack: () => void;
}

function AdmissionDetail({ item, onBack }: AdmissionDetailProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <Button variant="ghost" size="sm" onClick={onBack} className="-ml-2">
            <ArrowLeft className="mr-1 h-3 w-3" />
            Back to queue
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">
            {item.patient_name}
          </h1>
          <p className="text-muted-foreground font-mono text-sm">
            {item.patient_mrn}
          </p>
        </div>
        <Badge
          variant={
            item.waiting_days != null && item.waiting_days > 7
              ? "destructive"
              : "outline"
          }
        >
          Waiting {item.waiting_days ?? "—"} d
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Patient
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Birth date</span>
              <span>
                {formatDate(item.patient_birth_date)}
                {item.patient_age != null && (
                  <span className="ml-1 text-muted-foreground">
                    ({item.patient_age})
                  </span>
                )}
              </span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Sex</span>
              <span>{SEX_LABELS[item.patient_sex] ?? item.patient_sex}</span>
            </div>
            <Separator />
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Insurance policy</span>
              <span className="font-mono text-xs text-right">
                {item.patient_insurance_policy_number || "—"}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Cancer case
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Diagnosis</span>
              <span className="font-mono text-right">
                {item.diagnosis_code || "—"}
              </span>
            </div>
            <Separator />
            <div className="flex flex-col gap-1">
              <span className="text-muted-foreground">Description</span>
              <span>{item.diagnosis_text || "—"}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Stage</span>
              <span className="font-medium">{item.stage || "—"}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">TNM</span>
              <span className="font-mono">
                {item.tnm_t || "—"} {item.tnm_n || "—"} {item.tnm_m || "—"}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Queue
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Waiting since</span>
              <span>{formatDateTime(item.waiting_since)}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Waiting days</span>
              <span className="font-medium">{item.waiting_days ?? "—"}</span>
            </div>
          </CardContent>
        </Card>

        {(item.last_consilium_date ||
          item.last_consilium_decision ||
          item.last_consilium_recommended_plan) && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                Last consilium
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {item.last_consilium_date && (
                <>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Date</span>
                    <span>{formatDateTime(item.last_consilium_date)}</span>
                  </div>
                  <Separator />
                </>
              )}
              {item.last_consilium_decision && (
                <>
                  <div className="flex flex-col gap-1">
                    <span className="text-muted-foreground">Decision</span>
                    <span className="whitespace-pre-wrap">
                      {item.last_consilium_decision}
                    </span>
                  </div>
                  <Separator />
                </>
              )}
              {item.last_consilium_recommended_plan && (
                <div className="flex flex-col gap-1">
                  <span className="text-muted-foreground">
                    Recommended plan
                  </span>
                  <span className="whitespace-pre-wrap">
                    {item.last_consilium_recommended_plan}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Available actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CaseTransitionButtons
            caseId={item.id}
            currentStatus="waiting_hospitalization"
          />
        </CardContent>
      </Card>
    </div>
  );
}
