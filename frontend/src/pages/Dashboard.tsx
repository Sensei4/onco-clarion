import { useEffect, useState } from "react";
import { useAuth } from "@/features/auth/useAuth";
import { fetchHealth, type HealthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Dashboard() {
  const { user } = useAuth();
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
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.full_name || user?.username}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Backend status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {loading && <p className="text-muted-foreground">Checking…</p>}
            {error && (
              <p className="text-destructive text-sm">Error: {error}</p>
            )}
            {health && (
              <p className="text-sm text-green-600 dark:text-green-400">
                {health.status} — {health.service}
              </p>
            )}
            <Button onClick={loadHealth} disabled={loading} size="sm">
              {loading ? "Checking…" : "Re-check"}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Coming next
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Cancer cases, events, and the full patient flow.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
