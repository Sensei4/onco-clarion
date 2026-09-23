import { useState } from "react";
import { BarChart3 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BarChart } from "@/features/reports/components/BarChart";
import {
  useCasesByStage,
  useCasesByStatus,
  useEventsByType,
  useTopDiagnoses,
  useWaitingTime,
} from "@/features/reports/hooks";
import type { ReportDateParams } from "@/features/reports/types";

const STATUS_COLORS: Record<string, string> = {
  new: "hsl(215, 15%, 65%)",
  diagnostic: "hsl(200, 80%, 55%)",
  consilium: "hsl(265, 70%, 60%)",
  waiting_hospitalization: "hsl(35, 90%, 55%)",
  in_treatment: "hsl(280, 70%, 55%)",
  observation: "hsl(150, 60%, 45%)",
  remission: "hsl(140, 70%, 40%)",
  relapse: "hsl(15, 85%, 55%)",
  terminal: "hsl(0, 75%, 50%)",
};

const STAGE_COLORS: Record<string, string> = {
  I: "hsl(140, 60%, 45%)",
  II: "hsl(80, 60%, 45%)",
  III: "hsl(35, 90%, 50%)",
  IV: "hsl(0, 75%, 50%)",
  unknown: "hsl(215, 15%, 60%)",
};

export function Reports() {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const params: ReportDateParams = {
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  };

  const casesByStatus = useCasesByStatus(params);
  const casesByStage = useCasesByStage(params);
  const eventsByType = useEventsByType(params);
  const topDiagnoses = useTopDiagnoses(params);
  const waitingTime = useWaitingTime();

  function clearDates() {
    setDateFrom("");
    setDateTo("");
  }

  const hasDateFilter = dateFrom || dateTo;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">
            Aggregated metrics from your organization's data
          </p>
        </div>
        <div className="flex items-end gap-3 flex-wrap">
          <div className="space-y-1">
            <Label htmlFor="date_from" className="text-xs">
              From
            </Label>
            <Input
              id="date_from"
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="date_to" className="text-xs">
              To
            </Label>
            <Input
              id="date_to"
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="h-9"
            />
          </div>
          {hasDateFilter && (
            <Button variant="outline" size="sm" onClick={clearDates}>
              Clear
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Cases by status */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Cases by status
            </CardTitle>
            <CardDescription>
              {casesByStatus.data
                ? `Total: ${casesByStatus.data.total}`
                : "Loading…"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {casesByStatus.isLoading && (
              <p className="text-muted-foreground">Loading…</p>
            )}
            {casesByStatus.isError && (
              <p className="text-destructive">Error loading report</p>
            )}
            {casesByStatus.data && (
              <BarChart
                items={casesByStatus.data.results.map((r) => ({
                  label: r.label,
                  value: r.count,
                  color: STATUS_COLORS[r.status],
                }))}
              />
            )}
          </CardContent>
        </Card>

        {/* Cases by stage */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Cases by stage
            </CardTitle>
            <CardDescription>
              {casesByStage.data
                ? `Total: ${casesByStage.data.total}`
                : "Loading…"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {casesByStage.isLoading && (
              <p className="text-muted-foreground">Loading…</p>
            )}
            {casesByStage.data && (
              <BarChart
                items={casesByStage.data.results.map((r) => ({
                  label: r.stage === "unknown" ? "Unknown" : `Stage ${r.stage}`,
                  value: r.count,
                  color: STAGE_COLORS[r.stage],
                }))}
              />
            )}
          </CardContent>
        </Card>

        {/* Waiting time summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Waiting time (hospitalization)
            </CardTitle>
            <CardDescription>
              {waitingTime.data
                ? `${waitingTime.data.total} case${waitingTime.data.total === 1 ? "" : "s"} waiting`
                : "Loading…"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {waitingTime.data && waitingTime.data.total === 0 && (
              <p className="text-muted-foreground text-sm">
                No cases currently waiting for hospitalization.
              </p>
            )}
            {waitingTime.data && waitingTime.data.total > 0 && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-muted-foreground text-xs uppercase">
                      Avg
                    </p>
                    <p className="text-2xl font-bold">
                      {waitingTime.data.avg_days}
                      <span className="text-sm font-normal text-muted-foreground">
                        {" "}
                        d
                      </span>
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs uppercase">
                      Median
                    </p>
                    <p className="text-2xl font-bold">
                      {waitingTime.data.median_days}
                      <span className="text-sm font-normal text-muted-foreground">
                        {" "}
                        d
                      </span>
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs uppercase">
                      Max
                    </p>
                    <p className="text-2xl font-bold">
                      {waitingTime.data.max_days}
                      <span className="text-sm font-normal text-muted-foreground">
                        {" "}
                        d
                      </span>
                    </p>
                  </div>
                </div>
                {waitingTime.data.top.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-xs uppercase text-muted-foreground">
                      Top waiting cases
                    </p>
                    <ul className="space-y-1 text-sm">
                      {waitingTime.data.top.slice(0, 5).map((c) => (
                        <li
                          key={c.case_id}
                          className="flex justify-between gap-2"
                        >
                          <span className="truncate">
                            {c.patient_name}{" "}
                            <span className="font-mono text-xs text-muted-foreground">
                              ({c.patient_mrn})
                            </span>
                          </span>
                          <Badge variant="destructive">
                            {c.waiting_days} d
                          </Badge>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Events by type */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Events by type
            </CardTitle>
            <CardDescription>
              {eventsByType.data
                ? `Total: ${eventsByType.data.total}`
                : "Loading…"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {eventsByType.data && (
              <BarChart
                items={eventsByType.data.results.map((r) => ({
                  label: r.label,
                  value: r.count,
                }))}
              />
            )}
          </CardContent>
        </Card>

        {/* Top diagnoses */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Top diagnoses
            </CardTitle>
            <CardDescription>ICD-O-3 codes</CardDescription>
          </CardHeader>
          <CardContent>
            {topDiagnoses.data && topDiagnoses.data.results.length === 0 && (
              <p className="text-muted-foreground text-sm">
                No diagnoses recorded.
              </p>
            )}
            {topDiagnoses.data && topDiagnoses.data.results.length > 0 && (
              <BarChart
                items={topDiagnoses.data.results.map((r) => ({
                  label: r.diagnosis_code,
                  value: r.count,
                }))}
              />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-6 text-sm text-muted-foreground flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Reports use your organization's data only. Date filter applies to
          cases-by-status, cases-by-stage, events-by-type, and top-diagnoses.
        </CardContent>
      </Card>
    </div>
  );
}
