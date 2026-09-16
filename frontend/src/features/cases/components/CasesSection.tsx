import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { CaseFormDialog } from "@/features/cases/components/CaseFormDialog";
import { useCases } from "@/features/cases/hooks";
import type { CaseStatus } from "@/features/cases/types";

interface CasesSectionProps {
  patientId: number;
  organizationId: number;
}

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
  waiting_hospitalization: "Waiting",
  in_treatment: "In treatment",
  observation: "Observation",
  remission: "Remission",
  relapse: "Relapse",
  terminal: "Terminal",
};

function formatDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function CasesSection({ patientId, organizationId }: CasesSectionProps) {
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data, isLoading, isError, error } = useCases({
    patient: patientId,
    page_size: 50,
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Cancer cases
        </CardTitle>
        <Button size="sm" onClick={() => setDialogOpen(true)}>
          <Plus className="mr-1 h-3 w-3" />
          Add case
        </Button>
      </CardHeader>

      <CardContent className="p-0">
        {isLoading && (
          <div className="p-6 text-center text-muted-foreground">
            Loading cases…
          </div>
        )}

        {isError && (
          <div className="p-6 text-center text-destructive">
            Error: {error instanceof Error ? error.message : "Unknown error"}
          </div>
        )}

        {data && data.results.length === 0 && (
          <div className="p-6 text-center text-muted-foreground">
            No cancer cases yet. Add the first one.
          </div>
        )}

        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Diagnosis</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((c) => (
                <TableRow key={c.id} className="cursor-pointer hover:bg-accent">
                  <TableCell className="font-medium">
                    <Link
                      to={`/cases/${c.id}`}
                      className="block hover:underline"
                    >
                      {c.diagnosis_code || "—"}
                    </Link>
                  </TableCell>
                  <TableCell>{c.stage || "—"}</TableCell>
                  <TableCell>
                    <Badge variant={STATUS_VARIANTS[c.status]}>
                      {STATUS_LABELS[c.status]}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {formatDate(c.created_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <CaseFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        patientId={patientId}
        organizationId={organizationId}
      />
    </Card>
  );
}
