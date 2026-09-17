import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  CalendarDays,
  ClipboardList,
  Eye,
  Hotel,
  RefreshCw,
  Stethoscope,
  Users,
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
import { useEvents } from "@/features/events/hooks";
import type { CancerEvent, EventType } from "@/features/events/types";
import {
  dateRangeForDays,
  humanDateLabel,
  humanTimeLabel,
  localDateKey,
} from "@/lib/date";

const TYPE_META: Record<EventType, { label: string; icon: LucideIcon }> = {
  primary_visit: { label: "Primary visit", icon: Stethoscope },
  followup_visit: { label: "Follow-up visit", icon: CalendarDays },
  observation_visit: { label: "Observation visit", icon: Eye },
  consilium: { label: "Consilium", icon: Users },
  hospitalization: { label: "Hospitalization", icon: Hotel },
  treatment: { label: "Treatment", icon: ClipboardList },
};

const RANGE_OPTIONS = [
  { value: 1, label: "Today + 1 day" },
  { value: 7, label: "Today + 7 days" },
  { value: 14, label: "Today + 14 days" },
];

interface GroupedEvents {
  dateKey: string;
  label: string;
  events: CancerEvent[];
}

function groupByDay(events: CancerEvent[]): GroupedEvents[] {
  const groups = new Map<string, CancerEvent[]>();
  for (const e of events) {
    const key = localDateKey(e.scheduled_at);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(e);
  }

  return Array.from(groups.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, list]) => ({
      dateKey: key,
      label: humanDateLabel(list[0].scheduled_at),
      events: list.sort(
        (a, b) =>
          new Date(a.scheduled_at).getTime() -
          new Date(b.scheduled_at).getTime(),
      ),
    }));
}

export function Schedule() {
  const [daysAhead, setDaysAhead] = useState(7);

  const range = useMemo(() => dateRangeForDays(daysAhead), [daysAhead]);

  const { data, isLoading, isError, error, refetch, isFetching } = useEvents({
    status: "planned",
    scheduled_from: range.from,
    scheduled_to: range.to,
    page_size: 100,
  });

  const grouped = useMemo(() => (data ? groupByDay(data.results) : []), [data]);

  const total = data?.count ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Schedule</h1>
          <p className="text-muted-foreground">
            {isLoading
              ? "Loading…"
              : `${total} planned event${total === 1 ? "" : "s"} in the selected range`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={daysAhead}
            onChange={(e) => setDaysAhead(Number(e.target.value))}
            className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          >
            {RANGE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw
              className={`mr-1 h-3 w-3 ${isFetching ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </div>

      {isLoading && (
        <div className="text-muted-foreground">Loading schedule…</div>
      )}

      {isError && (
        <div className="text-destructive">
          Error: {error instanceof Error ? error.message : "Unknown error"}
        </div>
      )}

      {!isLoading && !isError && grouped.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            No planned events in the selected range.
          </CardContent>
        </Card>
      )}

      {grouped.map((group) => (
        <Card key={group.dateKey}>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              {group.label}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Time</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Patient</TableHead>
                  <TableHead>Diagnosis</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {group.events.map((e) => {
                  const meta = TYPE_META[e.type];
                  const Icon = meta.icon;
                  return (
                    <TableRow
                      key={e.id}
                      className="cursor-pointer hover:bg-accent"
                    >
                      <TableCell className="font-mono text-sm">
                        {humanTimeLabel(e.scheduled_at)}
                      </TableCell>
                      <TableCell className="font-medium">
                        <Link
                          to={`/cases/${e.case}`}
                          className="inline-flex items-center gap-2 hover:underline"
                        >
                          <Icon className="h-4 w-4 text-muted-foreground" />
                          {meta.label}
                        </Link>
                      </TableCell>
                      <TableCell className="text-sm">
                        <Link
                          to={`/patients/${e.patient}`}
                          className="hover:underline"
                        >
                          {e.patient_name}
                        </Link>
                        <span className="ml-2 font-mono text-xs text-muted-foreground">
                          ({e.patient_mrn})
                        </span>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {e.case_diagnosis || "—"}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{e.status}</Badge>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
