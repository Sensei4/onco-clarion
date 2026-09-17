import { useState } from "react";
import {
  CalendarDays,
  ClipboardList,
  Eye,
  Hotel,
  Plus,
  Stethoscope,
  Users,
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
import { EventFormDialog } from "@/features/events/components/EventFormDialog";
import { useEvents } from "@/features/events/hooks";
import type { EventStatus, EventType } from "@/features/events/types";

interface EventsSectionProps {
  caseId: number;
  patientId: number;
  organizationId: number;
}

const TYPE_META: Record<
  EventType,
  { label: string; icon: typeof Stethoscope }
> = {
  primary_visit: { label: "Primary visit", icon: Stethoscope },
  followup_visit: { label: "Follow-up visit", icon: CalendarDays },
  observation_visit: { label: "Observation visit", icon: Eye },
  consilium: { label: "Consilium", icon: Users },
  hospitalization: { label: "Hospitalization", icon: Hotel },
  treatment: { label: "Treatment", icon: ClipboardList },
};

const STATUS_VARIANTS: Record<
  EventStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  planned: "outline",
  done: "default",
  cancelled: "destructive",
};

function formatDateTime(iso: string): string {
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

function truncate(text: string, max = 60): string {
  if (!text) return "—";
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

const TYPE_FILTER_OPTIONS: { value: EventType | ""; label: string }[] = [
  { value: "", label: "All types" },
  { value: "primary_visit", label: "Primary visits" },
  { value: "followup_visit", label: "Follow-up visits" },
  { value: "observation_visit", label: "Observation visits" },
  { value: "consilium", label: "Consilia" },
  { value: "hospitalization", label: "Hospitalizations" },
  { value: "treatment", label: "Treatments" },
];

export function EventsSection({
  caseId,
  patientId,
  organizationId,
}: EventsSectionProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [typeFilter, setTypeFilter] = useState<EventType | "">("");

  const { data, isLoading, isError, error } = useEvents({
    case: caseId,
    page_size: 100,
    type: typeFilter || undefined,
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Events
        </CardTitle>
        <div className="flex items-center gap-2">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as EventType | "")}
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
            Add event
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {isLoading && (
          <div className="p-6 text-center text-muted-foreground">
            Loading events…
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
              ? "No events of this type."
              : "No events yet. Add the first one."}
          </div>
        )}

        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Scheduled</TableHead>
                <TableHead>Author</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((e) => {
                const meta = TYPE_META[e.type];
                const Icon = meta.icon;
                return (
                  <TableRow key={e.id} className="hover:bg-accent">
                    <TableCell className="font-medium">
                      <span className="inline-flex items-center gap-2">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        {meta.label}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANTS[e.status]}>
                        {e.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">
                      {formatDateTime(e.scheduled_at)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {e.author_name}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground max-w-xs">
                      {truncate(e.notes)}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <EventFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        caseId={caseId}
        patientId={patientId}
        organizationId={organizationId}
      />
    </Card>
  );
}
