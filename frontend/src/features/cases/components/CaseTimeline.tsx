import type { StatusTransition } from "@/features/cases/types";

interface CaseTimelineProps {
  transitions: StatusTransition[];
}

const STATUS_LABELS: Record<string, string> = {
  new: "New",
  diagnostic: "Diagnostic",
  consilium: "Consilium",
  waiting_hospitalization: "Waiting for hospitalization",
  in_treatment: "In treatment",
  observation: "Observation",
  remission: "Remission",
  relapse: "Relapse",
  terminal: "Terminal",
};

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

export function CaseTimeline({ transitions }: CaseTimelineProps) {
  if (transitions.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No transitions recorded yet.
      </p>
    );
  }

  return (
    <ol className="relative space-y-4 border-l border-border pl-6">
      {transitions.map((t, index) => (
        <li key={t.id} className="relative">
          <span
            className={
              "absolute -left-7.25 top-1 flex h-3 w-3 items-center justify-center rounded-full border-2 border-background " +
              (index === 0 ? "bg-primary" : "bg-muted-foreground/40")
            }
            aria-hidden
          />
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="font-medium">
                {STATUS_LABELS[t.from_status] ?? t.from_status}
              </span>
              <span className="text-muted-foreground">→</span>
              <span className="font-medium">
                {STATUS_LABELS[t.to_status] ?? t.to_status}
              </span>
            </div>
            <div className="text-xs text-muted-foreground">
              {formatDateTime(t.transitioned_at)}
              {t.transitioned_by_name && (
                <>
                  {" · "}
                  <span>by {t.transitioned_by_name}</span>
                </>
              )}
            </div>
            {t.reason && (
              <p className="text-sm text-foreground/80 italic">“{t.reason}”</p>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
