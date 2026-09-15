import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Pencil } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { PatientEditDialog } from "@/features/patients/components/PatientEditDialog";
import { usePatient } from "@/features/patients/hooks";
import type { PatientSex } from "@/features/patients/types";

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

export function PatientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const patientId = id ? Number(id) : undefined;
  const [editOpen, setEditOpen] = useState(false);

  const { data: patient, isLoading, isError, error } = usePatient(patientId);

  if (isLoading) {
    return <div className="text-muted-foreground">Loading patient…</div>;
  }

  if (isError || !patient) {
    return (
      <div className="space-y-4">
        <div className="text-destructive">
          Error: {error instanceof Error ? error.message : "Patient not found"}
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
            to="/patients"
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="mr-1 h-3 w-3" />
            Back to patients
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">
            {patient.full_name}
          </h1>
          <p className="text-muted-foreground font-mono text-sm">
            {patient.medical_record_number}
          </p>
        </div>
        <Button onClick={() => setEditOpen(true)}>
          <Pencil className="mr-2 h-4 w-4" />
          Edit
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Demographics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Birth date</span>
              <span>{formatDate(patient.birth_date)}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Age</span>
              <span>{patient.age ?? "—"}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Sex</span>
              <span>{SEX_LABELS[patient.sex]}</span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Vital status</span>
              <Badge
                variant={
                  patient.vital_status === "alive" ? "default" : "destructive"
                }
              >
                {patient.vital_status}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Organization & record
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Organization</span>
              <span>{patient.organization_name}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span>{formatDateTime(patient.created_at)}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Updated</span>
              <span>{formatDateTime(patient.updated_at)}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Contacts
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm">
            {Object.keys(patient.contacts).length === 0 ? (
              <p className="text-muted-foreground">No contacts recorded.</p>
            ) : (
              <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto">
                {JSON.stringify(patient.contacts, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>
      </div>

      <PatientEditDialog
        patient={patient}
        open={editOpen}
        onOpenChange={setEditOpen}
      />
    </div>
  );
}
