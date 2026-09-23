import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "./useAuth";

/**
 * Renders children only if the current user is an admin or superuser.
 * Otherwise redirects to "/".
 */
export function RequireAdmin() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading…</p>
      </div>
    );
  }

  const isAdmin = user?.role === "admin" || user?.is_superuser === true;
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
