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
import {
  Icd11Search,
  type Icd11Selection,
} from "@/features/dictionaries/components/Icd11Search";
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

  // Initialize from existing data
  const [diagnosis, setDiagnosis] = useState<Icd11Selection | null>(
    caseData.icd11_mms_uri
      ? {
          uri: caseData.icd11_mms_uri,
          the_code: caseData.diagnosis_code,
          title: caseData.diagnosis_text,
        }
      : null,
  );
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
      setDiagnosis(
        caseData.icd11_mms_uri
          ? {
              uri: caseData.icd11_mms_uri,
              the_code: caseData.diagnosis_code,
              title: caseData.diagnosis_text,
            }
          : null,
      );
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
      icd11_mms_uri: diagnosis?.uri ?? "",
      diagnosis_code: diagnosis?.the_code ?? "",
      diagnosis_text: diagnosis?.title ?? "",
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
              <Label>Diagnosis (ICD-11)</Label>
              <Icd11Search
                value={diagnosis}
                onChange={setDiagnosis}
                placeholder="Search by code or name"
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
