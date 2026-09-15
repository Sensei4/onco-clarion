import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Search as SearchIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { PatientFormDialog } from "@/features/patients/components/PatientFormDialog";
import { usePatients } from "@/features/patients/hooks";
import type { PatientSex } from "@/features/patients/types";
import { useDebounce } from "@/hooks/useDebounce";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 20;

const SEX_LABELS: Record<PatientSex, string> = {
  male: "Male",
  female: "Female",
  other: "Other",
  unknown: "Unknown",
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

export function PatientsList() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);

  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading, isError, error, isFetching } = usePatients({
    page,
    page_size: PAGE_SIZE,
    search: debouncedSearch || undefined,
  });

  function handleSearchChange(value: string) {
    setSearch(value);
    setPage(1);
  }

  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 0;
  const hasPrev = data?.previous !== null && data?.previous !== undefined;
  const hasNext = data?.next !== null && data?.next !== undefined;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Patients</h1>
          <p className="text-muted-foreground">
            {data
              ? `${data.count} patient${data.count === 1 ? "" : "s"} in your organization`
              : "Loading…"}
          </p>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add patient
        </Button>
      </div>

      <div className="relative max-w-sm">
        <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search by name or MRN…"
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading && (
            <div className="p-8 text-center text-muted-foreground">
              Loading patients…
            </div>
          )}

          {isError && (
            <div className="p-8 text-center text-destructive">
              Error: {error instanceof Error ? error.message : "Unknown error"}
            </div>
          )}

          {data && data.results.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              {debouncedSearch
                ? `No patients match "${debouncedSearch}".`
                : "No patients yet. Add the first one."}
            </div>
          )}

          {data && data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Full name</TableHead>
                  <TableHead>MRN</TableHead>
                  <TableHead>Birth date</TableHead>
                  <TableHead>Sex</TableHead>
                  <TableHead>Vital status</TableHead>
                  <TableHead>Organization</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.results.map((patient) => (
                  <TableRow
                    key={patient.id}
                    className="cursor-pointer hover:bg-accent"
                  >
                    <TableCell className="font-medium">
                      <Link
                        to={`/patients/${patient.id}`}
                        className="block hover:underline"
                      >
                        {patient.full_name}
                      </Link>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {patient.medical_record_number}
                    </TableCell>
                    <TableCell>{formatDate(patient.birth_date)}</TableCell>
                    <TableCell>{SEX_LABELS[patient.sex]}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          patient.vital_status === "alive"
                            ? "default"
                            : "destructive"
                        }
                      >
                        {patient.vital_status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {patient.organization_name}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {data && data.count > 0 && (
        <div className="flex items-center justify-between text-sm">
          <p
            className={cn("text-muted-foreground", isFetching && "opacity-50")}
          >
            Page {page} of {totalPages || 1}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!hasPrev || isFetching}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasNext || isFetching}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      <PatientFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={() => setPage(1)}
      />
    </div>
  );
}
