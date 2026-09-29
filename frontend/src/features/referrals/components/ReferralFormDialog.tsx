import { useEffect, useMemo, useState, type FormEvent } from "react";

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
import {
  useCreateReferral,
  useDiagnosticDepartments,
} from "@/features/referrals/hooks";
import type {
  CreateReferralPayload,
  DiagnosticCategory,
} from "@/features/referrals/types";
import { ApiRequestError } from "@/lib/api";

interface ReferralFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  caseId: number;
  organizationId: number;
  onSuccess?: () => void;
}

function categoryLabel(category: DiagnosticCategory): string {
  const labels: Record<DiagnosticCategory, string> = {
    laboratory: "Laboratory",
    pathology: "Pathology / Morphology",
    imaging: "Radiology / Imaging",
    endoscopy: "Endoscopy",
    functional: "Functional diagnostics",
    surgery: "Day surgery",
    molecular: "Molecular diagnostics",
    other: "Other",
  };
  return labels[category] ?? category;
}

export function ReferralFormDialog({
  open,
  onOpenChange,
  caseId,
  organizationId,
  onSuccess,
}: ReferralFormDialogProps) {
  const createReferral = useCreateReferral();
  const { data: departmentsData, isLoading: departmentsLoading } =
    useDiagnosticDepartments();

  const [departmentId, setDepartmentId] = useState<number | null>(null);
  const [methodId, setMethodId] = useState<number | null>(null);
  const [scheduledAt, setScheduledAt] = useState("");
  const [room, setRoom] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  const departments = useMemo(
    () => departmentsData?.results ?? [],
    [departmentsData],
  );

  // Methods for the selected department
  const availableMethods = useMemo(() => {
    if (!departmentId) return [];
    const dept = departments.find((d) => d.id === departmentId);
    return dept?.methods ?? [];
  }, [departmentId, departments]);

  // Reset on close
  useEffect(() => {
    if (!open) {
      setDepartmentId(null);
      setMethodId(null);
      setScheduledAt("");
      setRoom("");
      setNotes("");
      setError(null);
    }
  }, [open]);

  // Reset method when department changes
  useEffect(() => {
    setMethodId(null);
  }, [departmentId]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!departmentId) {
      setError("Please select a department.");
      return;
    }

    const payload: CreateReferralPayload = {
      case: caseId,
      organization: organizationId,
      department: departmentId,
      method: methodId,
      scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : null,
      room: room.trim(),
      notes: notes.trim(),
    };

    try {
      await createReferral.mutateAsync(payload);
      onOpenChange(false);
      onSuccess?.();
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }
  }

  const selectClass =
    "w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring disabled:opacity-50";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add referral</DialogTitle>
            <DialogDescription>
              Request a diagnostic procedure for this case.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto pr-2">
            <div className="space-y-2">
              <Label htmlFor="referral_department">Department *</Label>
              <select
                id="referral_department"
                value={departmentId ?? ""}
                onChange={(e) =>
                  setDepartmentId(
                    e.target.value ? Number(e.target.value) : null,
                  )
                }
                className={selectClass}
                disabled={departmentsLoading}
                required
              >
                <option value="">
                  {departmentsLoading ? "Loading…" : "Select department…"}
                </option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({categoryLabel(d.category)})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_method">Method</Label>
              <select
                id="referral_method"
                value={methodId ?? ""}
                onChange={(e) =>
                  setMethodId(e.target.value ? Number(e.target.value) : null)
                }
                className={selectClass}
                disabled={!departmentId || availableMethods.length === 0}
              >
                <option value="">
                  {!departmentId
                    ? "Select department first"
                    : availableMethods.length === 0
                      ? "No methods in this department"
                      : "Select method (optional)…"}
                </option>
                {availableMethods.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.code ? `[${m.code}] ${m.name}` : m.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground">
                The referral title is auto-filled from the method name.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_scheduled_at">
                Scheduled at{" "}
                <span className="text-muted-foreground">(optional)</span>
              </Label>
              <Input
                id="referral_scheduled_at"
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_room">
                Room <span className="text-muted-foreground">(optional)</span>
              </Label>
              <Input
                id="referral_room"
                value={room}
                onChange={(e) => setRoom(e.target.value)}
                placeholder="e.g. 312"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_notes">
                Notes <span className="text-muted-foreground">(optional)</span>
              </Label>
              <textarea
                id="referral_notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                placeholder="Clinical indication, special instructions…"
              />
            </div>

            {error && (
              <div className="rounded-md border border-destructive bg-destructive/10 p-3">
                <p className="text-destructive text-sm">{error}</p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createReferral.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createReferral.isPending || !departmentId}
            >
              {createReferral.isPending ? "Creating…" : "Create referral"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
