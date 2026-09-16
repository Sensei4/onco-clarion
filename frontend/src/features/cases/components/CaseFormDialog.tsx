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
import { useCreateCase } from "@/features/cases/hooks";
import type { CreateCasePayload } from "@/features/cases/types";
import { ApiRequestError } from "@/lib/api";

interface CaseFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  patientId: number;
  organizationId: number;
  onSuccess?: () => void;
}

export function CaseFormDialog({
  open,
  onOpenChange,
  patientId,
  organizationId,
  onSuccess,
}: CaseFormDialogProps) {
  const createCase = useCreateCase();

  const [diagnosisCode, setDiagnosisCode] = useState("");
  const [diagnosisText, setDiagnosisText] = useState("");
  const [verificationDate, setVerificationDate] = useState("");
  const [tnmT, setTnmT] = useState("");
  const [tnmN, setTnmN] = useState("");
  const [tnmM, setTnmM] = useState("");
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setDiagnosisCode("");
      setDiagnosisText("");
      setVerificationDate("");
      setTnmT("");
      setTnmN("");
      setTnmM("");
      setStage("");
      setError(null);
    }
  }, [open]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const payload: CreateCasePayload = {
      patient: patientId,
      organization: organizationId,
      diagnosis_code: diagnosisCode.trim(),
      diagnosis_text: diagnosisText.trim(),
      verification_date: verificationDate || null,
      tnm_t: tnmT.trim(),
      tnm_n: tnmN.trim(),
      tnm_m: tnmM.trim(),
      stage: stage.trim(),
    };

    try {
      await createCase.mutateAsync(payload);
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add cancer case</DialogTitle>
            <DialogDescription>
              Create a new cancer case for this patient. You can refine the
              details later.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto pr-2">
            <div className="space-y-2">
              <Label htmlFor="diagnosis_code">
                Diagnosis code{" "}
                <span className="text-muted-foreground">
                  (ICD-O-3 / ICD-10)
                </span>
              </Label>
              <Input
                id="diagnosis_code"
                value={diagnosisCode}
                onChange={(e) => setDiagnosisCode(e.target.value)}
                placeholder="C50.9"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="diagnosis_text">Diagnosis (free text)</Label>
              <Input
                id="diagnosis_text"
                value={diagnosisText}
                onChange={(e) => setDiagnosisText(e.target.value)}
                placeholder="Breast cancer, unspecified"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="verification_date">Verification date</Label>
              <Input
                id="verification_date"
                type="date"
                value={verificationDate}
                onChange={(e) => setVerificationDate(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-2">
                <Label htmlFor="tnm_t">T</Label>
                <Input
                  id="tnm_t"
                  value={tnmT}
                  onChange={(e) => setTnmT(e.target.value)}
                  placeholder="T2"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tnm_n">N</Label>
                <Input
                  id="tnm_n"
                  value={tnmN}
                  onChange={(e) => setTnmN(e.target.value)}
                  placeholder="N1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tnm_m">M</Label>
                <Input
                  id="tnm_m"
                  value={tnmM}
                  onChange={(e) => setTnmM(e.target.value)}
                  placeholder="M0"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="stage">Stage</Label>
              <Input
                id="stage"
                value={stage}
                onChange={(e) => setStage(e.target.value)}
                placeholder="IIB"
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
              disabled={createCase.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createCase.isPending}>
              {createCase.isPending ? "Creating…" : "Create case"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
