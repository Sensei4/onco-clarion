import { useEffect, useState } from "react";
import { useAuth } from "@/features/auth/useAuth";
import { fetchHealth, type HealthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function Dashboard() {
  const { user, logout } = useAuth();
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
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">OncoClarion</h1>
            <p className="text-muted-foreground">
              Signed in as {user?.full_name || user?.username}
            </p>
          </div>
          <Button variant="outline" onClick={() => logout()}>
            Sign out
          </Button>
        </header>

        <div className="bg-card text-card-foreground rounded-lg border shadow-sm p-6 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Backend status
          </h2>
          {loading && <p className="text-muted-foreground">Checking…</p>}
          {error && <p className="text-destructive text-sm">Error: {error}</p>}
          {health && (
            <p className="text-sm text-green-600 dark:text-green-400">
              {health.status} — {health.service}
            </p>
          )}
          <Button onClick={loadHealth} disabled={loading}>
            {loading ? "Checking…" : "Re-check"}
          </Button>
        </div>

        <div className="bg-card text-card-foreground rounded-lg border shadow-sm p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-2">
            Coming next
          </h2>
          <p className="text-sm text-muted-foreground">
            Patients, CancerCases, Events, and the queues.
          </p>
        </div>
      </div>
    </div>
  );
}
