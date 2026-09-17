import { Link } from "react-router-dom";
import { RefreshCw } from "lucide-react";

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
import { useObservationList } from "@/features/cases/hooks";

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

function daysSince(iso: string | null): number | null {
  if (!iso) return null;
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return null;
  const now = Date.now();
  return Math.floor((now - then) / (1000 * 60 * 60 * 24));
}

function lastVisitLabel(days: number | null): string {
  if (days === null) return "never";
  if (days === 0) return "today";
  if (days === 1) return "1 day ago";
  return `${days} days ago`;
}

export function Observation() {
  const { data, isLoading, isError, error, refetch, isFetching } =
    useObservationList();

  const total = data?.length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Observation</h1>
          <p className="text-muted-foreground">
            {isLoading
              ? "Loading…"
              : `${total} case${total === 1 ? "" : "s"} under observation`}
          </p>
        </div>
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

      {isLoading && (
        <div className="text-muted-foreground">Loading observation list…</div>
      )}

      {isError && (
        <div className="text-destructive">
          Error: {error instanceof Error ? error.message : "Unknown error"}
        </div>
      )}

      {!isLoading && !isError && total === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            No cases under observation.
          </CardContent>
        </Card>
      )}

      {!isLoading && !isError && total > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Ordered by time since last visit (longest first)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patient</TableHead>
                  <TableHead>Diagnosis</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Last visit</TableHead>
                  <TableHead>Next visit</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data!.map((c) => {
                  const days = daysSince(c.last_visit_at);
                  return (
                    <TableRow
                      key={c.id}
                      className="cursor-pointer hover:bg-accent"
                    >
                      <TableCell className="font-medium">
                        <Link
                          to={`/cases/${c.id}`}
                          className="block hover:underline"
                        >
                          {c.patient_name}
                        </Link>
                        <span className="font-mono text-xs text-muted-foreground">
                          {c.patient_mrn}
                        </span>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {c.diagnosis_code || "—"}
                      </TableCell>
                      <TableCell>{c.stage || "—"}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            days !== null && days > 90
                              ? "destructive"
                              : "outline"
                          }
                        >
                          {lastVisitLabel(days)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {c.next_visit_at ? (
                          formatDateTime(c.next_visit_at)
                        ) : (
                          <span className="text-destructive">
                            not scheduled
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
