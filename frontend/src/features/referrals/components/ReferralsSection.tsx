import { useState } from "react";
import {
  FlaskConical,
  Microscope,
  Plus,
  Scan,
  Stethoscope,
  type LucideIcon,
} from "lucide-react";

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
import { ReferralDetailDialog } from "@/features/referrals/components/ReferralDetailDialog";
import { ReferralFormDialog } from "@/features/referrals/components/ReferralFormDialog";
import { useReferral, useReferrals } from "@/features/referrals/hooks";
import type { ReferralStatus, ReferralType } from "@/features/referrals/types";

interface ReferralsSectionProps {
  caseId: number;
  organizationId: number;
}

const TYPE_META: Record<ReferralType, { label: string; icon: LucideIcon }> = {
  lab: { label: "Laboratory", icon: FlaskConical },
  histology: { label: "Histology", icon: Microscope },
  cytology: { label: "Cytology", icon: Microscope },
  imaging: { label: "Imaging", icon: Scan },
  other: { label: "Other", icon: Stethoscope },
};

const STATUS_VARIANTS: Record<
  ReferralStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  ordered: "outline",
  completed: "default",
  cancelled: "destructive",
};

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

const TYPE_FILTER_OPTIONS: { value: ReferralType | ""; label: string }[] = [
  { value: "", label: "All types" },
  { value: "lab", label: "Laboratory" },
  { value: "histology", label: "Histology" },
  { value: "cytology", label: "Cytology" },
  { value: "imaging", label: "Imaging" },
  { value: "other", label: "Other" },
];

export function ReferralsSection({
  caseId,
  organizationId,
}: ReferralsSectionProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [typeFilter, setTypeFilter] = useState<ReferralType | "">("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data, isLoading, isError, error } = useReferrals({
    case: caseId,
    page_size: 100,
    type: typeFilter || undefined,
  });

  const { data: selectedReferral } = useReferral(selectedId ?? undefined);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Referrals
        </CardTitle>
        <div className="flex items-center gap-2">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as ReferralType | "")}
            className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          >
            {TYPE_FILTER_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <Button size="sm" onClick={() => setDialogOpen(true)}>
            <Plus className="mr-1 h-3 w-3" />
            Add referral
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {isLoading && (
          <div className="p-6 text-center text-muted-foreground">
            Loading referrals…
          </div>
        )}

        {isError && (
          <div className="p-6 text-center text-destructive">
            Error: {error instanceof Error ? error.message : "Unknown error"}
          </div>
        )}

        {data && data.results.length === 0 && (
          <div className="p-6 text-center text-muted-foreground">
            {typeFilter
              ? "No referrals of this type."
              : "No referrals yet. Add the first one."}
          </div>
        )}

        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ordered</TableHead>
                <TableHead>Result</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((r) => {
                const meta = TYPE_META[r.type];
                const Icon = meta.icon;
                return (
                  <TableRow
                    key={r.id}
                    className="cursor-pointer hover:bg-accent"
                    onClick={() => setSelectedId(r.id)}
                  >
                    <TableCell className="font-medium">
                      <span className="inline-flex items-center gap-2">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        {meta.label}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm">{r.title || "—"}</TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANTS[r.status]}>
                        {r.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(r.ordered_at)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground max-w-xs">
                      {r.status === "completed"
                        ? formatDate(r.result_received_at)
                        : "—"}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <ReferralFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        caseId={caseId}
        organizationId={organizationId}
      />

      <ReferralDetailDialog
        referral={selectedReferral ?? null}
        open={selectedId !== null}
        onOpenChange={(o) => !o && setSelectedId(null)}
      />
    </Card>
  );
}
