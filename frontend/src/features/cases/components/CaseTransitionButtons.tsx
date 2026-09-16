import { useState } from "react";
import { ArrowRight } from "lucide-react";

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
import { useTransitionCase } from "@/features/cases/hooks";
import type { CaseStatus } from "@/features/cases/types";
import { ApiRequestError } from "@/lib/api";

interface CaseTransitionButtonsProps {
  caseId: number;
  currentStatus: CaseStatus;
}

interface TransitionDef {
  action: string;
  label: string;
  target: CaseStatus;
  variant?: "default" | "destructive" | "outline" | "secondary";
}

/**
 * Frontend mirror of the backend FSM.
 *
 * This map only drives the UI (which buttons to show).
 * The backend enforces the real transition rules and returns 409
 * if a transition is not allowed.
 */
const TRANSITIONS_BY_STATUS: Record<CaseStatus, TransitionDef[]> = {
  new: [
    {
      action: "start_diagnostics",
      label: "Start diagnostics",
      target: "diagnostic",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  diagnostic: [
    {
      action: "schedule_consilium",
      label: "Schedule consilium",
      target: "consilium",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  consilium: [
    {
      action: "approve_hospitalization",
      label: "Approve hospitalization",
      target: "waiting_hospitalization",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  waiting_hospitalization: [
    {
      action: "admit_to_hospital",
      label: "Admit to hospital",
      target: "in_treatment",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  in_treatment: [
    {
      action: "complete_treatment",
      label: "Complete treatment",
      target: "observation",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  observation: [
    { action: "mark_remission", label: "Mark remission", target: "remission" },
    {
      action: "mark_relapse",
      label: "Mark relapse",
      target: "relapse",
      variant: "destructive",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  remission: [
    {
      action: "mark_relapse",
      label: "Mark relapse",
      target: "relapse",
      variant: "destructive",
    },
  ],
  relapse: [
    {
      action: "reschedule_consilium",
      label: "Reschedule consilium",
      target: "consilium",
    },
    {
      action: "mark_terminal",
      label: "Mark terminal",
      target: "terminal",
      variant: "destructive",
    },
  ],
  terminal: [],
};

export function CaseTransitionButtons({
  caseId,
  currentStatus,
}: CaseTransitionButtonsProps) {
  const transitions = TRANSITIONS_BY_STATUS[currentStatus] ?? [];
  const transitionCase = useTransitionCase(caseId);

  const [pending, setPending] = useState<TransitionDef | null>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  function openDialog(t: TransitionDef) {
    setPending(t);
    setReason("");
    setError(null);
  }

  function closeDialog() {
    setPending(null);
    setReason("");
    setError(null);
  }

  async function confirm() {
    if (!pending) return;
    setError(null);
    try {
      await transitionCase.mutateAsync({
        action: pending.action,
        reason: reason.trim(),
      });
      closeDialog();
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }
  }

  if (transitions.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No further transitions available.
      </p>
    );
  }

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {transitions.map((t) => (
          <Button
            key={t.action}
            variant={t.variant ?? "default"}
            size="sm"
            onClick={() => openDialog(t)}
            disabled={transitionCase.isPending}
          >
            <ArrowRight className="mr-1 h-3 w-3" />
            {t.label}
          </Button>
        ))}
      </div>

      <Dialog open={pending !== null} onOpenChange={(o) => !o && closeDialog()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{pending?.label}</DialogTitle>
            <DialogDescription>
              This will move the case status from{" "}
              <span className="font-mono">{currentStatus}</span> to{" "}
              <span className="font-mono">{pending?.target}</span>.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2 py-4">
            <Label htmlFor="reason">Reason (optional)</Label>
            <textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="e.g. Board approved, patient admitted to ward 3…"
            />
            {error && (
              <p className="text-destructive text-sm" role="alert">
                {error}
              </p>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={closeDialog}
              disabled={transitionCase.isPending}
            >
              Cancel
            </Button>
            <Button onClick={confirm} disabled={transitionCase.isPending}>
              {transitionCase.isPending ? "Applying…" : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
