import { useEffect, useState } from "react";
import { CheckCircle2, RotateCcw, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  useCancelReferral,
  useCompleteReferral,
  useReopenReferral,
} from "@/features/referrals/hooks";
import type {
  ReferralDetail,
  ReferralStatus,
  ReferralType,
} from "@/features/referrals/types";
import { ApiRequestError } from "@/lib/api";

interface ReferralDetailDialogProps {
  referral: ReferralDetail | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const TYPE_LABELS: Record<ReferralType, string> = {
  lab: "Laboratory test",
  histology: "Histology",
  cytology: "Cytology",
  imaging: "Imaging",
  other: "Other",
};

const STATUS_VARIANTS: Record<
  ReferralStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  ordered: "outline",
  completed: "default",
  cancelled: "destructive",
};

function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

type Mode = "view" | "complete" | "cancel";

export function ReferralDetailDialog({
  referral,
  open,
  onOpenChange,
}: ReferralDetailDialogProps) {
  const [mode, setMode] = useState<Mode>("view");
  const [resultText, setResultText] = useState("");
  const [cancelReason, setCancelReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  const completeReferral = useCompleteReferral(referral?.id ?? 0);
  const cancelReferral = useCancelReferral(referral?.id ?? 0);
  const reopenReferral = useReopenReferral(referral?.id ?? 0);

  useEffect(() => {
    if (!open) {
      setMode("view");
      setResultText("");
      setCancelReason("");
      setError(null);
    }
  }, [open]);

  if (!referral) return null;

  const isPending =
    completeReferral.isPending ||
    cancelReferral.isPending ||
    reopenReferral.isPending;

  async function handleComplete() {
    setError(null);
    try {
      await completeReferral.mutateAsync({ result_text: resultText.trim() });
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiRequestError) setError(err.detail);
      else setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  async function handleCancel() {
    setError(null);
    try {
      await cancelReferral.mutateAsync({ reason: cancelReason.trim() });
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiRequestError) setError(err.detail);
      else setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  async function handleReopen() {
    setError(null);
    try {
      await reopenReferral.mutateAsync();
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiRequestError) setError(err.detail);
      else setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {referral.title || TYPE_LABELS[referral.type]}
          </DialogTitle>
          <DialogDescription>
            {TYPE_LABELS[referral.type]} · Case{" "}
            {referral.case_diagnosis || `#${referral.case}`}
          </DialogDescription>
        </DialogHeader>

        {mode === "view" && (
          <div className="space-y-4 py-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Status</span>
              <Badge variant={STATUS_VARIANTS[referral.status]}>
                {referral.status}
              </Badge>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Ordered by</span>
              <span>{referral.ordered_by_name}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Ordered at</span>
              <span>{formatDateTime(referral.ordered_at)}</span>
            </div>
            {referral.notes && (
              <>
                <Separator />
                <div className="flex flex-col gap-1">
                  <span className="text-muted-foreground">Notes</span>
                  <span className="whitespace-pre-wrap">{referral.notes}</span>
                </div>
              </>
            )}
            {referral.status === "completed" && (
              <>
                <Separator />
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Result received</span>
                  <span>{formatDateTime(referral.result_received_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Completed by</span>
                  <span>{referral.completed_by_name || "—"}</span>
                </div>
                {referral.result_text && (
                  <div className="flex flex-col gap-1">
                    <span className="text-muted-foreground">Result</span>
                    <span className="whitespace-pre-wrap rounded-md bg-muted p-3">
                      {referral.result_text}
                    </span>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {mode === "complete" && (
          <div className="space-y-3 py-4">
            <Label htmlFor="result_text">Result</Label>
            <textarea
              id="result_text"
              value={resultText}
              onChange={(e) => setResultText(e.target.value)}
              rows={4}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="Describe the result of the procedure…"
              autoFocus
            />
            {error && (
              <p className="text-destructive text-sm" role="alert">
                {error}
              </p>
            )}
          </div>
        )}

        {mode === "cancel" && (
          <div className="space-y-3 py-4">
            <Label htmlFor="cancel_reason">Reason (optional)</Label>
            <textarea
              id="cancel_reason"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              rows={3}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="Why is this referral being cancelled?"
              autoFocus
            />
            {error && (
              <p className="text-destructive text-sm" role="alert">
                {error}
              </p>
            )}
          </div>
        )}

        <DialogFooter className="flex-wrap gap-2">
          {mode === "view" && referral.status === "ordered" && (
            <>
              <Button
                variant="outline"
                onClick={() => setMode("cancel")}
                disabled={isPending}
              >
                <XCircle className="mr-1 h-4 w-4" />
                Cancel referral
              </Button>
              <Button onClick={() => setMode("complete")} disabled={isPending}>
                <CheckCircle2 className="mr-1 h-4 w-4" />
                Complete
              </Button>
            </>
          )}
          {mode === "view" &&
            (referral.status === "completed" ||
              referral.status === "cancelled") && (
              <Button
                variant="outline"
                onClick={handleReopen}
                disabled={isPending}
              >
                <RotateCcw className="mr-1 h-4 w-4" />
                Reopen
              </Button>
            )}
          {mode === "complete" && (
            <>
              <Button
                variant="outline"
                onClick={() => setMode("view")}
                disabled={isPending}
              >
                Back
              </Button>
              <Button onClick={handleComplete} disabled={isPending}>
                {isPending ? "Saving…" : "Save result"}
              </Button>
            </>
          )}
          {mode === "cancel" && (
            <>
              <Button
                variant="outline"
                onClick={() => setMode("view")}
                disabled={isPending}
              >
                Back
              </Button>
              <Button
                variant="destructive"
                onClick={handleCancel}
                disabled={isPending}
              >
                {isPending ? "Cancelling…" : "Confirm cancel"}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
