import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useUpdatePatient } from "@/features/patients/hooks";
import type {
  PatientDetail,
  PatientSex,
  PatientVitalStatus,
  UpdatePatientPayload,
} from "@/features/patients/types";
import { ApiRequestError } from "@/lib/api";

interface PatientEditDialogProps {
  patient: PatientDetail;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SEX_OPTIONS: { value: PatientSex; label: string }[] = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "other", label: "Other" },
  { value: "unknown", label: "Unknown" },
];

const VITAL_OPTIONS: { value: PatientVitalStatus; label: string }[] = [
  { value: "alive", label: "Alive" },
  { value: "dead", label: "Dead" },
];

export function PatientEditDialog({
  patient,
  open,
  onOpenChange,
}: PatientEditDialogProps) {
  const updatePatient = useUpdatePatient(patient.id);

  const [fullName, setFullName] = useState(patient.full_name);
  const [birthDate, setBirthDate] = useState(patient.birth_date);
  const [sex, setSex] = useState<PatientSex>(patient.sex);
  const [mrn, setMrn] = useState(patient.medical_record_number);
  const [vitalStatus, setVitalStatus] = useState<PatientVitalStatus>(
    patient.vital_status,
  );
  const [error, setError] = useState<string | null>(null);

  // Reset form when patient changes or dialog reopens
  useEffect(() => {
    if (open) {
      setFullName(patient.full_name);
      setBirthDate(patient.birth_date);
      setSex(patient.sex);
      setMrn(patient.medical_record_number);
      setVitalStatus(patient.vital_status);
      setError(null);
    }
  }, [open, patient]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const payload: UpdatePatientPayload = {
      full_name: fullName.trim(),
      birth_date: birthDate,
      sex,
      medical_record_number: mrn.trim(),
      vital_status: vitalStatus,
    };

    try {
      await updatePatient.mutateAsync(payload);
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit patient</DialogTitle>
            <DialogDescription>
              Update patient information. Organization cannot be changed.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit_full_name">Full name</Label>
              <Input
                id="edit_full_name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_birth_date">Birth date</Label>
              <Input
                id="edit_birth_date"
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_sex">Sex</Label>
              <select
                id="edit_sex"
                value={sex}
                onChange={(e) => setSex(e.target.value as PatientSex)}
                className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                {SEX_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_mrn">Medical record number</Label>
              <Input
                id="edit_mrn"
                value={mrn}
                onChange={(e) => setMrn(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_vital_status">Vital status</Label>
              <select
                id="edit_vital_status"
                value={vitalStatus}
                onChange={(e) =>
                  setVitalStatus(e.target.value as PatientVitalStatus)
                }
                className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                {VITAL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {error && (
              <p className="text-destructive text-sm" role="alert">
                {error}
              </p>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={updatePatient.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updatePatient.isPending}>
              {updatePatient.isPending ? "Saving…" : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
