import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  ApiRequestError,
  fetchMe,
  login as apiLogin,
  logout as apiLogout,
  type LoginPayload,
  type User,
} from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const me = await fetchMe();
      setUser(me);
    } catch (e) {
      if (e instanceof ApiRequestError && e.status === 403) {
        setUser(null);
      } else {
        setError(e instanceof Error ? e.message : "Unknown error");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = useCallback(async (payload: LoginPayload) => {
    setError(null);
    const me = await apiLogin(payload);
    setUser(me);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, error, login, logout, refresh }),
    [user, loading, error, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
