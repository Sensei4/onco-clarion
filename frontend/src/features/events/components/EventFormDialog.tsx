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
import { useCreateEvent } from "@/features/events/hooks";
import type {
  CreateEventPayload,
  EventStatus,
  EventType,
  TreatmentModality,
} from "@/features/events/types";
import { ApiRequestError } from "@/lib/api";
import { cn } from "@/lib/utils";

interface EventFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  caseId: number;
  patientId: number;
  organizationId: number;
  /** If set, type is fixed and no type selector is shown. */
  fixedType?: EventType;
  /** Optional users available as consilium participants. */
  availableUsers?: { id: number; username: string; full_name: string }[];
  onSuccess?: () => void;
}

const EVENT_TYPE_OPTIONS: { value: EventType; label: string }[] = [
  { value: "primary_visit", label: "Primary visit" },
  { value: "followup_visit", label: "Follow-up visit" },
  { value: "observation_visit", label: "Observation visit" },
  { value: "consilium", label: "Consilium" },
  { value: "hospitalization", label: "Hospitalization" },
  { value: "treatment", label: "Treatment" },
];

const STATUS_OPTIONS: { value: EventStatus; label: string }[] = [
  { value: "planned", label: "Planned" },
  { value: "done", label: "Done" },
  { value: "cancelled", label: "Cancelled" },
];

const MODALITY_OPTIONS: { value: TreatmentModality; label: string }[] = [
  { value: "chemo", label: "Chemotherapy" },
  { value: "radiation", label: "Radiation therapy" },
  { value: "surgery", label: "Surgery" },
  { value: "targeted", label: "Targeted therapy" },
  { value: "immunotherapy", label: "Immunotherapy" },
  { value: "other", label: "Other" },
];

export function EventFormDialog({
  open,
  onOpenChange,
  caseId,
  patientId,
  organizationId,
  fixedType,
  availableUsers = [],
  onSuccess,
}: EventFormDialogProps) {
  const [type, setType] = useState<EventType>(fixedType ?? "primary_visit");
  const createEvent = useCreateEvent(type);

  // Common
  const [status, setStatus] = useState<EventStatus>("planned");
  const [scheduledAt, setScheduledAt] = useState("");
  const [occurredAt, setOccurredAt] = useState("");
  const [notes, setNotes] = useState("");

  // Primary visit
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [physicalExam, setPhysicalExam] = useState("");

  // Follow-up / observation
  const [findings, setFindings] = useState("");
  const [plan, setPlan] = useState("");

  // Consilium
  const [participantIds, setParticipantIds] = useState<number[]>([]);
  const [decision, setDecision] = useState("");
  const [recommendedPlan, setRecommendedPlan] = useState("");

  // Hospitalization
  const [ward, setWard] = useState("");
  const [reason, setReason] = useState("");
  const [dischargeDate, setDischargeDate] = useState("");

  // Treatment
  const [modality, setModality] = useState<TreatmentModality>("chemo");
  const [regimen, setRegimen] = useState("");
  const [cycleNumber, setCycleNumber] = useState("");
  const [cycleTotal, setCycleTotal] = useState("");
  const [drugs, setDrugs] = useState("");

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    // Reset on open
    setStatus("planned");
    setScheduledAt("");
    setOccurredAt("");
    setNotes("");
    setChiefComplaint("");
    setPhysicalExam("");
    setFindings("");
    setPlan("");
    setParticipantIds([]);
    setDecision("");
    setRecommendedPlan("");
    setWard("");
    setReason("");
    setDischargeDate("");
    setModality("chemo");
    setRegimen("");
    setCycleNumber("");
    setCycleTotal("");
    setDrugs("");
    setError(null);
    if (fixedType) setType(fixedType);
  }, [open, fixedType]);

  function toggleParticipant(id: number) {
    setParticipantIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id],
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!scheduledAt) {
      setError("Scheduled date and time is required.");
      return;
    }

    const payload: CreateEventPayload = {
      case: caseId,
      patient: patientId,
      organization: organizationId,
      status,
      scheduled_at: new Date(scheduledAt).toISOString(),
      occurred_at: occurredAt ? new Date(occurredAt).toISOString() : null,
      notes: notes.trim(),
    };

    // Subtype-specific
    if (type === "primary_visit") {
      payload.chief_complaint = chiefComplaint.trim();
      payload.physical_exam = physicalExam.trim();
    } else if (type === "followup_visit") {
      payload.findings = findings.trim();
      payload.plan = plan.trim();
    } else if (type === "observation_visit") {
      payload.findings = findings.trim();
    } else if (type === "consilium") {
      payload.participants = participantIds;
      payload.decision = decision.trim();
      payload.recommended_plan = recommendedPlan.trim();
    } else if (type === "hospitalization") {
      payload.ward = ward.trim();
      payload.reason = reason.trim();
      payload.discharge_date = dischargeDate || null;
    } else if (type === "treatment") {
      payload.modality = modality;
      payload.regimen = regimen.trim();
      payload.cycle_number = cycleNumber ? Number(cycleNumber) : null;
      payload.cycle_total = cycleTotal ? Number(cycleTotal) : null;
      payload.drugs = drugs.trim();
    }

    try {
      await createEvent.mutateAsync(payload);
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
      <DialogContent className="sm:max-w-2xl">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add event</DialogTitle>
            <DialogDescription>
              Record a clinical event in this cancer case.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4 max-h-[65vh] overflow-y-auto pr-2">
            {/* Type + Status */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="event_type">Type</Label>
                <select
                  id="event_type"
                  value={type}
                  onChange={(e) => setType(e.target.value as EventType)}
                  disabled={!!fixedType}
                  className={cn(selectClass, fixedType && "opacity-60")}
                >
                  {EVENT_TYPE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="event_status">Status</Label>
                <select
                  id="event_status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value as EventStatus)}
                  className={selectClass}
                >
                  {STATUS_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Schedule */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="scheduled_at">Scheduled at</Label>
                <Input
                  id="scheduled_at"
                  type="datetime-local"
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="occurred_at">Occurred at (optional)</Label>
                <Input
                  id="occurred_at"
                  type="datetime-local"
                  value={occurredAt}
                  onChange={(e) => setOccurredAt(e.target.value)}
                />
              </div>
            </div>

            {/* Type-specific */}

            {type === "primary_visit" && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="chief_complaint">Chief complaint</Label>
                  <textarea
                    id="chief_complaint"
                    value={chiefComplaint}
                    onChange={(e) => setChiefComplaint(e.target.value)}
                    rows={2}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="physical_exam">Physical exam</Label>
                  <textarea
                    id="physical_exam"
                    value={physicalExam}
                    onChange={(e) => setPhysicalExam(e.target.value)}
                    rows={2}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
              </>
            )}

            {(type === "followup_visit" || type === "observation_visit") && (
              <div className="space-y-2">
                <Label htmlFor="findings">Findings</Label>
                <textarea
                  id="findings"
                  value={findings}
                  onChange={(e) => setFindings(e.target.value)}
                  rows={2}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                />
              </div>
            )}

            {type === "followup_visit" && (
              <div className="space-y-2">
                <Label htmlFor="plan">Plan</Label>
                <textarea
                  id="plan"
                  value={plan}
                  onChange={(e) => setPlan(e.target.value)}
                  rows={2}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                />
              </div>
            )}

            {type === "consilium" && (
              <>
                <div className="space-y-2">
                  <Label>Participants</Label>
                  <div className="rounded-md border border-input p-2 max-h-32 overflow-y-auto space-y-1">
                    {availableUsers.length === 0 && (
                      <p className="text-sm text-muted-foreground">
                        No users available.
                      </p>
                    )}
                    {availableUsers.map((u) => (
                      <label
                        key={u.id}
                        className="flex items-center gap-2 text-sm cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={participantIds.includes(u.id)}
                          onChange={() => toggleParticipant(u.id)}
                        />
                        <span>{u.full_name || u.username}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="decision">Decision</Label>
                  <textarea
                    id="decision"
                    value={decision}
                    onChange={(e) => setDecision(e.target.value)}
                    rows={2}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="recommended_plan">Recommended plan</Label>
                  <textarea
                    id="recommended_plan"
                    value={recommendedPlan}
                    onChange={(e) => setRecommendedPlan(e.target.value)}
                    rows={2}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
              </>
            )}

            {type === "hospitalization" && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="ward">Ward</Label>
                  <Input
                    id="ward"
                    value={ward}
                    onChange={(e) => setWard(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reason">Reason</Label>
                  <textarea
                    id="reason"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    rows={2}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="discharge_date">
                    Discharge date (optional)
                  </Label>
                  <Input
                    id="discharge_date"
                    type="date"
                    value={dischargeDate}
                    onChange={(e) => setDischargeDate(e.target.value)}
                  />
                </div>
              </>
            )}

            {type === "treatment" && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label htmlFor="modality">Modality</Label>
                    <select
                      id="modality"
                      value={modality}
                      onChange={(e) =>
                        setModality(e.target.value as TreatmentModality)
                      }
                      className={selectClass}
                    >
                      {MODALITY_OPTIONS.map((o) => (
                        <option key={o.value} value={o.value}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="regimen">Regimen</Label>
                    <Input
                      id="regimen"
                      value={regimen}
                      onChange={(e) => setRegimen(e.target.value)}
                      placeholder="AC, FOLFOX, …"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label htmlFor="cycle_number">Cycle number</Label>
                    <Input
                      id="cycle_number"
                      type="number"
                      min={1}
                      value={cycleNumber}
                      onChange={(e) => setCycleNumber(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cycle_total">Cycle total</Label>
                    <Input
                      id="cycle_total"
                      type="number"
                      min={1}
                      value={cycleTotal}
                      onChange={(e) => setCycleTotal(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="drugs">Drugs and doses</Label>
                  <textarea
                    id="drugs"
                    value={drugs}
                    onChange={(e) => setDrugs(e.target.value)}
                    rows={2}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
              </>
            )}

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
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
              disabled={createEvent.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createEvent.isPending}>
              {createEvent.isPending ? "Creating…" : "Create event"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
