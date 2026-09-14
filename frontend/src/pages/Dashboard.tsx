import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadHealth() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <div className="max-w-md w-full bg-card text-card-foreground rounded-lg border shadow-sm p-8 space-y-4">
        <h1 className="text-3xl font-bold tracking-tight">OncoClarion</h1>
        <p className="text-muted-foreground">
          Open-source software for oncology patient flow.
        </p>

        <div className="border-t pt-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide mb-2 text-muted-foreground">
            Backend status
          </h2>
          {loading && <p className="text-muted-foreground">Checking…</p>}
          {error && <p className="text-destructive text-sm">Error: {error}</p>}
          {health && (
            <p className="text-sm text-green-600 dark:text-green-400">
              {health.status} — {health.service}
            </p>
          )}
        </div>

        <Button onClick={loadHealth} disabled={loading}>
          {loading ? "Checking…" : "Re-check"}
        </Button>
      </div>
    </div>
  );
}
