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
import { useCreateReferral } from "@/features/referrals/hooks";
import type {
  CreateReferralPayload,
  ReferralType,
} from "@/features/referrals/types";
import { ApiRequestError } from "@/lib/api";

interface ReferralFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  caseId: number;
  organizationId: number;
  onSuccess?: () => void;
}

const TYPE_OPTIONS: { value: ReferralType; label: string }[] = [
  { value: "lab", label: "Laboratory test" },
  { value: "histology", label: "Histology" },
  { value: "cytology", label: "Cytology" },
  { value: "imaging", label: "Imaging" },
  { value: "other", label: "Other" },
];

export function ReferralFormDialog({
  open,
  onOpenChange,
  caseId,
  organizationId,
  onSuccess,
}: ReferralFormDialogProps) {
  const createReferral = useCreateReferral();

  const [type, setType] = useState<ReferralType>("lab");
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setType("lab");
      setTitle("");
      setNotes("");
      setError(null);
    }
  }, [open]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const payload: CreateReferralPayload = {
      case: caseId,
      organization: organizationId,
      type,
      title: title.trim(),
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
    "w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add referral</DialogTitle>
            <DialogDescription>
              Request a diagnostic procedure for this case.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="referral_type">Type</Label>
              <select
                id="referral_type"
                value={type}
                onChange={(e) => setType(e.target.value as ReferralType)}
                className={selectClass}
              >
                {TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_title">Title</Label>
              <Input
                id="referral_title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. CT chest with contrast"
                autoFocus
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_notes">Notes</Label>
              <textarea
                id="referral_notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                placeholder="Clinical indication, instructions…"
              />
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
              disabled={createReferral.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createReferral.isPending}>
              {createReferral.isPending ? "Creating…" : "Create referral"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
