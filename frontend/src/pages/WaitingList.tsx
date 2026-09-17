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
import { useWaitingList } from "@/features/cases/hooks";

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

function waitingLabel(days: number | null): string {
  if (days === null) return "—";
  if (days === 0) return "today";
  if (days === 1) return "1 day";
  return `${days} days`;
}

export function WaitingList() {
  const { data, isLoading, isError, error, refetch, isFetching } =
    useWaitingList();

  const total = data?.length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Waiting list</h1>
          <p className="text-muted-foreground">
            {isLoading
              ? "Loading…"
              : `${total} case${total === 1 ? "" : "s"} waiting for hospitalization`}
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
        <div className="text-muted-foreground">Loading waiting list…</div>
      )}

      {isError && (
        <div className="text-destructive">
          Error: {error instanceof Error ? error.message : "Unknown error"}
        </div>
      )}

      {!isLoading && !isError && total === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            No cases are waiting for hospitalization.
          </CardContent>
        </Card>
      )}

      {!isLoading && !isError && total > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Ordered by waiting time (longest first)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patient</TableHead>
                  <TableHead>Diagnosis</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Waiting since</TableHead>
                  <TableHead>Waiting</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data!.map((c) => (
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
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(c.waiting_since)}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          c.waiting_days !== null && c.waiting_days > 7
                            ? "destructive"
                            : "outline"
                        }
                      >
                        {waitingLabel(c.waiting_days)}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
