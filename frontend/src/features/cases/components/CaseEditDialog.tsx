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
import { useUpdateCase } from "@/features/cases/hooks";
import type {
  CancerCaseDetail,
  UpdateCasePayload,
} from "@/features/cases/types";
import { ApiRequestError } from "@/lib/api";

interface CaseEditDialogProps {
  caseData: CancerCaseDetail;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CaseEditDialog({
  caseData,
  open,
  onOpenChange,
}: CaseEditDialogProps) {
  const updateCase = useUpdateCase(caseData.id);

  const [diagnosisCode, setDiagnosisCode] = useState(caseData.diagnosis_code);
  const [diagnosisText, setDiagnosisText] = useState(caseData.diagnosis_text);
  const [verificationDate, setVerificationDate] = useState(
    caseData.verification_date ?? "",
  );
  const [tnmT, setTnmT] = useState(caseData.tnm_t);
  const [tnmN, setTnmN] = useState(caseData.tnm_n);
  const [tnmM, setTnmM] = useState(caseData.tnm_m);
  const [stage, setStage] = useState(caseData.stage);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setDiagnosisCode(caseData.diagnosis_code);
      setDiagnosisText(caseData.diagnosis_text);
      setVerificationDate(caseData.verification_date ?? "");
      setTnmT(caseData.tnm_t);
      setTnmN(caseData.tnm_n);
      setTnmM(caseData.tnm_m);
      setStage(caseData.stage);
      setError(null);
    }
  }, [open, caseData]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const payload: UpdateCasePayload = {
      diagnosis_code: diagnosisCode.trim(),
      diagnosis_text: diagnosisText.trim(),
      verification_date: verificationDate || null,
      tnm_t: tnmT.trim(),
      tnm_n: tnmN.trim(),
      tnm_m: tnmM.trim(),
      stage: stage.trim(),
    };

    try {
      await updateCase.mutateAsync(payload);
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
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit cancer case</DialogTitle>
            <DialogDescription>
              Update diagnosis, staging, and verification information.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto pr-2">
            <div className="space-y-2">
              <Label htmlFor="edit_diagnosis_code">
                Diagnosis code{" "}
                <span className="text-muted-foreground">
                  (ICD-O-3 / ICD-10)
                </span>
              </Label>
              <Input
                id="edit_diagnosis_code"
                value={diagnosisCode}
                onChange={(e) => setDiagnosisCode(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_diagnosis_text">Diagnosis (free text)</Label>
              <Input
                id="edit_diagnosis_text"
                value={diagnosisText}
                onChange={(e) => setDiagnosisText(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_verification_date">Verification date</Label>
              <Input
                id="edit_verification_date"
                type="date"
                value={verificationDate}
                onChange={(e) => setVerificationDate(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-2">
                <Label htmlFor="edit_tnm_t">T</Label>
                <Input
                  id="edit_tnm_t"
                  value={tnmT}
                  onChange={(e) => setTnmT(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit_tnm_n">N</Label>
                <Input
                  id="edit_tnm_n"
                  value={tnmN}
                  onChange={(e) => setTnmN(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit_tnm_m">M</Label>
                <Input
                  id="edit_tnm_m"
                  value={tnmM}
                  onChange={(e) => setTnmM(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_stage">Stage</Label>
              <Input
                id="edit_stage"
                value={stage}
                onChange={(e) => setStage(e.target.value)}
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
              disabled={updateCase.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updateCase.isPending}>
              {updateCase.isPending ? "Saving…" : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
