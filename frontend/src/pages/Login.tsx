import { useState, type FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/features/auth/useAuth";
import { ApiRequestError } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface LocationState {
  from?: { pathname: string };
}

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login({ username, password });
      const redirectTo = state?.from?.pathname ?? "/";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <form
        onSubmit={handleSubmit}
        className="max-w-sm w-full bg-card text-card-foreground rounded-lg border shadow-sm p-8 space-y-4"
      >
        <div>
          <h1 className="text-2xl font-bold tracking-tight">OncoClarion</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Sign in to continue
          </p>
        </div>

        <div className="space-y-2">
          <label htmlFor="username" className="text-sm font-medium">
            Username
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        {error && (
          <p className="text-destructive text-sm" role="alert">
            {error}
          </p>
        )}

        <Button type="submit" className="w-full" disabled={submitting}>
          {submitting ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </div>
  );
}
